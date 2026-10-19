---
layout: post
title: 'When the Autoscaler Lies to the Scheduler: How AI Workloads are Breaking and
  Rebuilding Kubernetes'
date: 2026-10-19 18:14:37 +0530
categories: Tech
excerpt: When distributed AI workloads trigger expensive GPU provisioning, architectural
  mismatches between Kubernetes autoscalers and schedulers can leave nodes idle. Here
  is why decoupled control loops fail modern accelerator clusters.
cover_image: /assets/images/posts/default-cover.png
cover_caption: Abstract visualization of decoupled Kubernetes control loops managing
  distributed GPU nodes.
---

{% raw %}
At 2:00 AM, a batch distributed training job for a 70-billion-parameter open-weight model is submitted to an enterprise Kubernetes cluster. The job requires 32 GPUs distributed across four discrete nodes, connected by high-bandwidth interconnects. Almost immediately, the cluster autoscaler detects the unscheduled pods, evaluates the available cloud node groups, and triggers the spin-up of four brand-new, expensive GPU instances. The cloud provider provisions the virtual machines, the `kubelet` initializes, the nodes report `Ready`, and the cloud billing meter begins running at roughly $40 to $80 per hour per instance.

Then, nothing happens.

The pods remain stuck in `Pending`. Hours pass. Tens of thousands of dollars of compute run completely idle because the pods cannot be scheduled onto the very nodes that were provisioned specifically for them. By dawn, what should have been a routine training run has morphed into a high-visibility incident of wasted infrastructure budget. 

This failure mode is becoming distressingly common across platform engineering teams. For over a decade, Kubernetes relied on a fundamental design premise: compute resources are homogeneous, stateless microservices can be scheduled piecemeal, and coarse resource requests—like CPU millicores and memory mebibytes—are sufficient to capture an application’s physical requirements.

Modern distributed AI workloads have shattered this model. As organizations transition toward standardizing their open-weight AI infrastructure (a shift we explored in our analysis of the [Kubernetes moment for open-weight AI infrastructure](/tech/2026/07/26/kubernetes-moment-open-weight-ai-infrastructure.html)), the historical abstraction layers of Kubernetes are struggling. The silent killer of accelerator clusters is an architectural rift: the cluster autoscaler runs an abstracted simulation of node capacity, while the scheduler makes deterministic decisions based on micro-architectural hardware realities. When the autoscaler lies to the scheduler, the entire cluster grinds to a halt.

---

## The Two-Loop Architectural Divide: Why the Classic Seam Fails

To diagnose why AI infrastructure deadlocks, we must dissect the historical separation of concerns between `kube-scheduler` and the `cluster-autoscaler`. Kubernetes was deliberately architected around decoupled, autonomous control loops.

```
       +-------------------------------------------------------+
       |                  Kubernetes Control Plane             |
       |                                                       |
       |   +-------------------+       +-------------------+   |
       |   |   kube-scheduler  |       | cluster-autoscaler|   |
       |   +---------+---------+       +---------+---------+   |
       |             |                           |             |
       |      Evaluates against           Simulates scheduling |
       |      real, registered            using generic, mock  |
       |      nodes & hardware            node templates       |
       |             |                           |             |
       |             v                           v             |
       |   +-------------------+       +-------------------+   |
       |   | Precise Topology/ |       | Requests Cloud VMs|   |
       |   | Filter Plugins    |       | (Out-of-Band)     |   |
       |   +-------------------+       +-------------------+   |
       +-------------------------------------------------------+
```

### The Division of Labor

Under the classic paradigm:
1. **`kube-scheduler`** is responsible for assignment. It continuously watches the API server for newly created pods without an assigned `nodeName`. It evaluates those pods against a known set of *already existing* nodes using a multi-phase framework: Filter, PreScore, Score, Reserve, Permit, PreBind, and Bind.
2. **`cluster-autoscaler`** is responsible for capacity provision. It watches for pods marked as unschedulable (specifically, those carrying a `PodCondition` of `PodScheduled = False` with a reason of `Unschedulable`). It does not run inside the scheduler; instead, it runs out-of-tree, repeatedly simulating whether adding a node from one of its pre-configured node templates would allow the pending pods to schedule.

### The Divergent Simulation Engine

The breakdown occurs inside the autoscaler's internal scheduling simulation. The autoscaler cannot execute the actual plugins compiled into `kube-scheduler`. Instead, it embeds a stripped-down, mock version of the scheduler's logic.

In a traditional environment running Go or Java microservices, this simulation works reliably. If a pod requests `2000m` CPU and `4Gi` memory, the autoscaler checks if a standard instance template has at least 2 vCPUs and 4 GiB available. If it does, it calls the cloud provider’s API to spawn the instance. When the node joins the cluster, `kube-scheduler` runs its real filter plugins, confirms the scalar integers match, and binds the pod.

With modern accelerator workloads, this assumption collapses. The autoscaler's simulator operates almost exclusively on coarse scalar capacities, while modern instances require deep hardware evaluation. The autoscaler looks at a node template, calculates that `nvidia.com/gpu: 8` matches the sum of pod requirements, and provisions the node. 

However, once the node registers, `kube-scheduler` executes specialized node-level filters—such as NUMA node affinity, PCIe topology alignments, or custom device plugin constraints. The scheduler determines that while the node possesses eight physical GPUs, they do not satisfy the specific architectural placement criteria requested by the workload. The scheduler rejects the placement. The node remains empty, the autoscaler assumes its job is done, and the pod sits in `Pending` forever.

---

## The Hardware Topology Wall: When Scalar Integers Fail

The primary reason the scheduler and the autoscaler fall out of sync is that legacy Kubernetes resource tracking models compute via scalar integers:

```yaml
resources:
  requests:
    cpu: "16"
    memory: "64Gi"
    nvidia.com/gpu: "4"
```

Requesting `nvidia.com/gpu: 4` conveys zero information about the underlying physical interconnectivity required to execute high-performance tensor-parallel operations.

### Interconnect Geometry and NVLink Meshes

In an 8-GPU system (such as an NVIDIA HGX H100/H200 or B200 configuration), GPUs are not arranged as independent, uniform devices on a single bus. They are wired together using specialized high-speed interconnect meshes (NVLink) managed by physical NVSwitches. 

```
  +--------+   NVLink   +--------+
  | GPU 0  |<=========>| GPU 1  |
  +---+----+            +----+---+
      |                      |
PCIe  |                      | PCIe
      v                      v
+------------+        +------------+
| PCIe Switch|        | PCIe Switch|
+-----+------+        +-----+------+
      |                      |
      +---------[ NUMA 0 ]---+
                   |
             Host CPU / RAM
```

Depending on the hardware design:
- GPUs 0 through 3 might share a direct, non-blocking NVLink domain.
- GPUs 4 through 7 might share a separate domain, or communicate cross-socket via host PCIe bridges.
- If an LLM inference engine using Tensor Parallelism (TP=4) requests 4 GPUs, and the scheduler naively assigns GPUs 0, 1, 4, and 5, inter-GPU communication must cross PCIe switches or CPU sockets. 

The resulting latency penalty can degrade training and inference throughput by 50% to 80%. Advanced scheduling plugins (such as those provided by specialized hardware vendors) will deliberately reject assignments that split across non-optimal topological boundaries. But the cluster autoscaler's simulator has no visibility into this mesh; it simply counts to four.

### NUMA and PCIe Bus Alignment

Accelerators do not operate in a vacuum—they rely heavily on direct memory access (DMA) paths to host memory and specialized network interfaces (such as 400Gb/s InfiniBand or RoCE adapters). Modern servers feature multiple Non-Uniform Memory Access (NUMA) nodes corresponding to physical CPU sockets.

If a pod's high-speed NIC is physically attached to the PCIe lanes of NUMA Node 0, but the scheduler binds the pod to GPUs physically wired to NUMA Node 1, every network packet transferred via GPUDirect RDMA must cross the interconnect bus (e.g., Ultra Path Interconnect). This introduces substantial jitter and memory latency. 

When Kubernetes cluster operators deploy the Node Resource Topology Matcher or Topology Manager with a `single-numa-node` policy, `kube-scheduler` strictly denies scheduling if a pod’s resource requests span multiple NUMA domains. The classic cluster autoscaler, unaware of these NUMA boundaries, repeatedly provisions standard instances that fail this validation.

### Device Partitioning and Virtual Slices

The scalar integer model degrades even further when dealing with partitioned devices, such as NVIDIA Multi-Instance GPU (MIG) or dynamic time-slicing. Under MIG, a physical A100 or H100 GPU can be carved into distinct hardware instances (e.g., `1g.10gb`, `3g.40gb`, `7g.80gb`), each with isolated compute cores, memory controllers, and crossbar paths.

| Slicing Model | Kubernetes Representation | Hardware Isolation | Autoscaler Failure Mode |
| :--- | :--- | :--- | :--- |
| **Full GPU** | `nvidia.com/gpu: 1` | Complete (Physical) | Ignores cross-GPU NVLink topology |
| **MIG (Static)** | `nvidia.com/mig-3g.40gb: 1` | Complete (Silicon) | Cannot predict unapplied geometry splits |
| **Time-Slicing** | Shared `nvidia.com/gpu` | None (Context-switching) | Leads to compute starvation under load |
| **DRA Claim** | `ResourceClaim` (Structured) | Configurable / Dynamic | Fully visible to DRA-aware schedulers |

If a node group contains instances capable of dynamic MIG repartitioning, the autoscaler cannot determine whether an instance can be sliced to satisfy three `1g.10gb` claims and one `3g.40gb` claim simultaneously. It sees a binary count of GPUs, creating a structural blind spot that classic Kubernetes abstractions cannot reconcile.

---

## Atomic Scaling and Gang Scheduling: Eliminating Partial Cluster Deadlocks

Microservice architectures depend on incremental scalability: if an HTTP service needs ten replicas, provisioning eight is strictly better than provisioning zero. Microservices handle traffic proportionally.

Distributed machine learning workloads operate under the exact opposite principle. They require **gang scheduling** (also known as all-or-nothing scheduling). In distributed frameworks like PyTorch (via `torchrun` or the Kubeflow Training Operator), training jobs use collective communication primitives like `AllReduce`. Every worker process must initialize, register with the rendezvous backend, and synchronize tensor gradients at the barrier of every training step.

### The Partial Placement Deadlock

Without gang scheduling tightly coupled to cluster autoscaling, partial placement deadlocks are virtually guaranteed in multi-tenant environments.

Consider two jobs submitted simultaneously:
* **Job A** requires 8 nodes.
* **Job B** requires 8 nodes.
* The cluster currently has 4 free nodes, and autoscaling is in progress to add 12 more.

`kube-scheduler`, acting independently on a per-pod basis, binds 4 pods of Job A to the currently available nodes. Job A cannot begin training because it still needs 4 more nodes. It enters a holding pattern, actively occupying those 4 nodes. 

Next, the autoscaler adds 4 more nodes. The scheduler immediately places 4 pods of Job B onto those newly provisioned nodes. Now, Job A is holding 4 nodes waiting for 4 more; Job B is holding 4 nodes waiting for 4 more. Both jobs sit completely idle, burning thousands of dollars of compute per day, deadlocked because neither can acquire its complete gang.

```
Node Pool Status:
+----------+----------+----------+----------+
|  Node 1  |  Node 2  |  Node 3  |  Node 4  |
|  [Job A] |  [Job A] |  [Job A] |  [Job A] | -> Waiting for 4 more nodes
+----------+----------+----------+----------+
|  Node 5  |  Node 6  |  Node 7  |  Node 8  |
|  [Job B] |  [Job B] |  [Job B] |  [Job B] | -> Waiting for 4 more nodes
+----------+----------+----------+----------+
RESULT: Complete Cluster Deadlock (0% Compute Efficiency)
```

### Kueue: Quota and Admission Control at the Batch Layer

To resolve this, the Kubernetes ecosystem has largely consolidated around **Kueue**, an upstream, job-level admission controller managed by SIG-Scheduling. 

Kueue introduces a structural barrier between the application submission layer and the Kubernetes scheduler. Instead of dumping raw pods directly onto `kube-scheduler`, distributed workloads (such as RayClusters, Kubeflow PyTorchJobs, or custom Batch Jobs) are submitted to Kueue as `Workloads`.

Kueue manages:
1. **Queueing and Prioritization**: Fair-sharing, preemption, and hierarchical resource quotas across multiple tenants.
2. **Gang Admission**: Ensuring that an entire workload's complement of pods is admitted to the scheduling queue *simultaneously*.
3. **Cluster Gating**: Kueue leverages pod scheduling gates (`spec.schedulingGates`). It keeps pods in a gated state—preventing `kube-scheduler` from evaluating or binding them piecemeal—until it verifies that aggregate cluster quota and capacity exist to run the entire group.

However, while Kueue solves the gang admission problem within the cluster, it traditionally faced an external hurdle: how does it inform the out-of-tree `cluster-autoscaler` that it needs to scale up capacity for a group of pods that are intentionally hidden behind scheduling gates? This friction led directly to the development of native structured resource models.

---

## Dynamic Resource Allocation (DRA): Reinventing the Device Abstraction

To permanently fix the architectural seam between the autoscaler and the scheduler, Kubernetes needed to replace the legacy Device Plugin framework. Introduced in Kubernetes 1.26 and significantly matured in subsequent releases, **Dynamic Resource Allocation (DRA)** completely restructures how hardware is modeled, discovered, and allocated.

### Moving Beyond Device Plugins

The traditional Device Plugin API was simple: a daemon on the node advertised an integer value to the `kubelet` (e.g., `nvidia.com/gpu: 8`), and returned an environment variable or device path mount (e.g., `/dev/nvidia0`) when assigned. The core Kubernetes scheduler remained entirely ignorant of what the hardware actually was.

DRA transforms this into an expressive, declarative model built on several key API primitives:
* **`ResourceSlice`**: Published by device drivers directly into the Kubernetes control plane. It contains detailed, structured data about every available physical device on a node—its NUMA affinity, PCIe address, model, interconnect topology, and available memory.
* **`DeviceClass`**: An administrative cluster-scoped resource that defines broad categories of hardware (e.g., `h100-nvlink-exclusive` or `l4-inference`) and provides selector mechanisms for workloads.
* **`ResourceClaim`**: An object referenced by a pod (or generated via a `ResourceClaimTemplate`) specifying the precise hardware attributes, constraints, and topological relationships the application requires.

### Structured Resource Parameters

Instead of requesting a scalar integer, a pod using DRA declares its hardware requirements using expressive structured parameters. Consider this example of an advanced `ResourceClaimTemplate`:

```yaml
apiVersion: resource.k8s.io/v1alpha3
kind: ResourceClaimTemplate
metadata:
  name: h100-nvlink-mesh
spec:
  spec:
    devices:
      requests:
      - name: gpu-group
        deviceClassName: nvidia-gpu
        count: 4
        selectors:
        - cel:
            expression: "device.attributes['model'] == 'H100-SXM5-80GB'"
        - cel:
            expression: "device.attributes['nvlink_generation'] >= 4"
      constraints:
      - requests: ["gpu-group"]
        matchAttribute: "interconnect.mesh_id"
```

In this specification:
1. The workload requests four devices matching a specific hardware architecture (`H100-SXM5-80GB`).
2. It uses Common Expression Language (CEL) to validate hardware attributes.
3. Critically, it specifies a constraint (`matchAttribute: "interconnect.mesh_id"`), mandating that all four devices share a common high-bandwidth interconnect fabric.

Because DRA stores these structured parameters directly within API objects in the control plane, `kube-scheduler` no longer relies on opaque device plugin calls during node binding. 

Crucially, **DRA-aware autoscalers** read these exact same `ResourceSlice` definitions and claims. The autoscaler's simulator is no longer guessing whether a node's GPUs will fit a pod; it inspects the structured claim, cross-references it with the node template's advertised `ResourceSlices`, and provisions infrastructure with deterministic confidence that the scheduler will approve the placement.

---

## Bridging the Seam: The ProvisioningRequest API in Action

While DRA addresses device description, platform engineers still needed an operational bridge to coordinate multi-node, gang-scheduled batch workloads with cloud-provider provisioning systems. That bridge is the **`ProvisioningRequest` API**, developed collaboratively by SIG-Scheduling and SIG-Autoscaling.

### The Contract-First Provisioning Model

Rather than forcing the autoscaler to deduce scaling needs by watching failing pods, the `ProvisioningRequest` API introduces an explicit, contract-first scaling protocol:

1. **Workload Submission**: A distributed framework submits a multi-pod job wrapped inside a batch queue like Kueue.
2. **Admission Validation**: Kueue determines that current cluster capacity cannot satisfy the job without exceeding active quotas or fracturing node topology.
3. **Request Creation**: Instead of immediately allowing the pods to fall through to `kube-scheduler` (which would trigger partial-placement deadlocks), Kueue creates a `ProvisioningRequest` Custom Resource (CR).
4. **Cloud Reservation**: The `cluster-autoscaler` reads the `ProvisioningRequest`. It bypasses internal pod-by-pod scheduling simulations, interfaces directly with cloud-provider capacity APIs (such as AWS EC2 Fleet, GCP Capacity Reservations, or Azure VMSS), and reserves the nodes atomically.
5. **Node Readiness Handshake**: Once all requested nodes are operational, labeled, and validated, the autoscaler updates the status of the `ProvisioningRequest` to `Provisioned`.
6. **Ungating and Binding**: Kueue observes the `Provisioned` status, un-gates the waiting pods, and presents them to `kube-scheduler`. The scheduler places the pods onto the pre-allocated nodes with zero churn.

```
[ Kueue Workload ] 
        |
        v  (Creates CR)
[ ProvisioningRequest ] <------- Watches ------- [ Cluster Autoscaler ]
        |                                                 |
        | (Status: Capacity Reserved)                     v (Calls Cloud API)
        +<====================================== [ Cloud Infrastructure ]
        |
        v  (Ungates Pods)
[ kube-scheduler ] ----------------------------> [ Binds Pods to Nodes ]
```

### Anatomy of a ProvisioningRequest Manifest

Below is an annotated example of how Kueue constructs a `ProvisioningRequest` to negotiate an atomic, multi-node scale-out:

```yaml
apiVersion: autoscaling.x-k8s.io/v1beta1
kind: ProvisioningRequest
metadata:
  name: distributed-training-run-042
  namespace: ml-training
spec:
  provisioningClassName: check-capacity.autoscaling.x-k8s.io
  parameters:
    maxRetries: "3"
    nodePoolName: "h100-sxm-pool"
  podTemplates:
    - count: 8
      template:
        spec:
          nodeSelector:
            node.kubernetes.io/instance-type: "p5.48xlarge"
            topology.kubernetes.io/zone: "us-east-1a"
          containers:
            - name: trainer
              image: registry.internal/models/trainer:v2.4
              resources:
                limits:
                  nvidia.com/gpu: "8"
                  memory: "1000Gi"
                  vpc.amazonaws.com/efa: "32"
```

In this workflow, the autoscaler does not treat the request as eight separate placement puzzles. It treats the `podTemplates` block as an **indivisible atomic unit**. If the cloud provider can only fulfill five nodes due to regional capacity shortages, the autoscaler aborts or fails the reservation without spinning up partial, orphan nodes. 

This contract-first handshake prevents clusters from acquiring half a distributed training cluster, saving organizations from burning cloud budgets on idle instances.

---

## Fleet Economics: Minimizing Cold Starts, Wasted Joules, and Accelerator Waste

Resolving the architectural disconnect between the scheduler and the autoscaler is not merely a matter of clean systems design; it is a vital economic and environmental necessity.

### The True Cost of Idle Compute

A standard 8-way modern accelerator instance costs between $30,000 and $45,000 per month on on-demand public cloud infrastructure. When an autoscaler provisions these instances, but the scheduler rejects the pods due to topology mismatch, the cluster incurs:
* **Direct Compute Waste**: Paying full hourly rates for high-spec instances that execute no compute instructions.
* **Secondary Infrastructure Sunk Costs**: Paying for idle high-throughput networked storage volumes, dedicated VPC interconnects, and high-bandwidth transit gateways provisioned alongside the nodes.
* **Engineering Velocity Degradation**: Upstream pipeline failures where training checkpoints fail to materialize and customer-facing inference engines fail their latency SLAs.

### Inference Cold Starts and Scale-to-Zero

While distributed training suffers from atomic deadlocks, LLM inference pipelines suffer heavily from cold-start latency. 

Modern production systems attempt to leverage dynamic scale-to-zero to minimize expenses during traffic lulls. However, an enterprise LLM serving pod can easily require 100 GiB of weights loaded across multiple tensor-parallel GPUs. 

If the autoscaler takes three minutes to provision a node, and the scheduler spends another two minutes rejecting candidates or waiting on out-of-order storage and topology plugins, client requests will time out. 

To bridge this, platform engineering teams are forced into over-provisioning hot standby nodes—effectively abandoning elastic scaling altogether. Aligning the autoscaler’s provisioning assumptions with the scheduler’s actual binding requirements enables deterministic, sub-minute instance acquisitions, allowing platforms to scale up reliably under load spikes.

### The Macro Energy Perspective

Beyond financial overhead, the energy consumption of AI infrastructure has become a primary bottleneck for data centers worldwide. An individual 8-GPU training node can draw between 6.5 kW and 10.2 kW under full load, and even idling nodes consume substantial baseline power to maintain memory retention and cooling fans.

As we analyzed in our reports on how the [tech industry moves towards efficient AI](/news/2026/07/23/tech-industry-moves-towards-efficient-ai.html) and how these demands impact [AI data centers and power grid stability](/news/2026/07/25/ai-data-centers-power-grid-stability.html), computational efficiency is no longer confined to algorithm design. Eliminating scheduler-autoscaler deadlocks directly prevents megawatts of unutilized energy from being drawn from strained power grids.

---

## Future Outlook: Unified Control Loops and Native Placement Primitives

The Kubernetes project is currently executing one of the most substantial architectural transitions in its history: dismantling the classic boundary between `kube-scheduler` and out-of-tree autoscalers.

```
Legacy Architecture (Decoupled, Reactive)
[ Pods Pending ] ---> [ cluster-autoscaler Simulates ] ---> [ Cloud API Spawns Node ] 
                                                                   |
[ Pods Evaluated ] <--- [ kube-scheduler Runs Real Plugins ] <----+
(Risk: Mismatch & Rejection)

Future Architecture (Unified Placement Primitives)
[ Pod / Workload ] ---> [ kube-scheduler with DRA & In-Tree Autoscaling Plugins ]
                                   |
         Directly queries Provisionable Capacity via Provider Providers
                                   |
                 [ Atomic Node Acquisition & Placement ]
```

Upstream initiatives led by SIG-Scheduling, SIG-Autoscaling, and the Batch Working Group are advancing toward several unified objectives:

1. **Retiring Post-Hoc Simulation**: The long-term roadmap envisions phasing out the autoscaler's fragile scheduling simulator entirely. Instead, `kube-scheduler` itself will expose extension points that evaluate *hypothetical* nodes natively, allowing the scheduler to tell the infrastructure provider precisely what instance shape, topology, and interconnect geometry it requires.
2. **Native Provisionable Capacity**: Future control planes will treat node acquisition as a native step within the scheduler's `Reserve` or `PreBind` phases. If a pod requires capacity that does not physically exist, the scheduler can invoke an in-tree provisioning hook directly, ensuring that what gets requested matches what can be bound.
3. **Cross-Zone Network Fabric Topology**: Next-generation Kubernetes APIs are expanding topology awareness beyond single-node NUMA domains to multi-rack InfiniBand rail architectures. Workloads will soon declare latency budgets across physical data center spine-leaf fabrics, allowing the scheduler and autoscaler to co-locate distributed jobs within identical network aggregation blocks.

### Key Architectural Takeaways for Platform Engineers

If you are managing or architecting Kubernetes infrastructure for modern AI/ML workloads today, relying on legacy `cpu`/`memory` scalar models and standalone cluster-autoscaler instances will eventually lead to production outages and runaway spend. To harden your platform:

* **Stop relying on vanilla scalar integer scheduling**: Migrate device allocations toward Dynamic Resource Allocation (DRA) as driver support solidifies across your hardware vendors.
* **Isolate batch and training workloads behind admission controllers**: Implement Kueue to enforce gang scheduling and prevent partial-placement deadlocks from reaching the cluster scheduler.
* **Adopt Contract-First Provisioning**: Use the `ProvisioningRequest` API pattern to coordinate atomic node group creation, ensuring that cloud infrastructure scale-ups are guaranteed to match workload constraints before pods are released.

The future of Kubernetes is not just about keeping microservices running; it is about building a deterministic control plane for high-performance distributed hardware. Bridging the gap between the autoscaler and the scheduler is the critical step toward making that vision a reality.
{% endraw %}
