---
layout: post
title: Semantic Search in C++ Without Python, Libtorch, or ONNX Runtime
date: 2026-09-06 04:14:30 +0530
categories: Tech
excerpt: Discover how to run transformer models and semantic search in native C++
  with a tiny binary footprint, bypassing Python and LibTorch entirely.
cover_image: /assets/images/posts/semantic-search-cxx-without-python-libtorch-cover.png
cover_caption: A conceptual diagram showing lightweight native C++ semantic search
  architecture using Kjarni
---

When you want to add semantic search, embeddings, or transformer-based text processing to a native C++ application, you traditionally face a frustrating architectural fork in the road. On one side, you can embed a Python interpreter via pybind11, bringing along a massive dependency tree of wheels, pip packages, and GIL management overhead. On the other side, you can link against heavyweight deep learning runtimes like LibTorch or ONNX Runtime. 

While LibTorch and ONNX Runtime are powerful, they come with significant baggage. Shipping a production binary backed by LibTorch often means bundling hundreds of megabytes of dynamic libraries just to calculate vector embeddings for a few search queries. For resource-constrained edge devices, embedded systems, or snappy desktop applications, this introduces severe memory bloat, high initialization latency, and a complex build pipeline that constantly fights with your CMake configurations.

If you are building high-performance systems where startup time, memory footprint, and deployment simplicity matter, this heavyweight dilemma is hard to swallow. What if you could run transformer models directly in native C++ with a binary size measured in kilobytes rather than hundreds of megabytes, completely bypassing Python, LibTorch, and ONNX Runtime?

## Introducing Kjarni: A Lean Native Inference Engine

This is where **Kjarni** enters the picture. Kjarni is a standalone C library paired with a modern C++ wrapper designed specifically to execute transformer models—such as text embeddings, classification, and cross-encoder reranking—without secondary runtime environments or interpreter overhead. 

The core philosophy behind Kjarni is radical minimalism combined with high performance. Instead of dragging in massive graph optimization engines, it provides a streamlined inference pipeline tailored for transformer architectures. The metrics speak for themselves: the core shared library weighs in at approximately **19.4 MB**, while a typical compiled binary utilizing the engine sits at a mere **283 KB**. 

Kjarni supports a wide array of popular transformer models out of the box, including:
- `minilm-l6-v2` (for fast, lightweight embeddings)
- `mpnet-base-v2` (for higher-fidelity semantic representations)
- `nomic-embed-text` (for flexible context lengths)
- `bge-m3` (for dense and sparse multilingual retrieval)

By stripping away the abstraction layers typical of general-purpose deep learning frameworks, Kjarni makes it trivial to drop transformer capabilities directly into native desktop utilities, local search indexes, and command-line tools without inflating your installer size.

## Architecture and ABI Design: Bridging C and C++23

Achieving this level of lightweight portability requires careful architectural separation. Kjarni solves this by decoupling its core inference engine behind a stable, pure C Application Binary Interface (`kjarni.h`) and layering a modern, header-only C++ wrapper (`kjarni.hpp`) on top.

```
+---------------------------------------------------+
|               Your Modern C++ App                 |
|             (Uses C++23 std::expected)            |
+---------------------------------------------------+
                          |
                          v
+---------------------------------------------------+
|            kjarni.hpp (Header-Only)               |
|         RAII, Type Safety, Modern Idioms          |
+---------------------------------------------------+
                          |
                          v
+---------------------------------------------------+
|               kjarni.h (Pure C ABI)               |
|         ABI Stability, Cross-Language Safe        |
+---------------------------------------------------+
                          |
                          v
+---------------------------------------------------+
|          Kjarni Native Shared Library             |
|                  (~19.4 MB)                       |
+---------------------------------------------------+
```

### The C ABI Foundation (`kjarni.h`)

The foundation of the library is written in pure C. This design choice guarantees maximum binary compatibility and ensures that the core engine can be safely loaded across different compilers and even bridged into other languages (such as C#, Go, or Python) if needed. It exposes explicit initialization, inference, and memory-freeing functions that prevent C++ name-mangling issues and runtime ABI mismatches.

### The Modern C++ Wrapper (`kjarni.hpp`)

If you are writing modern C++, interacting directly with raw C pointers and manual error codes quickly becomes tedious. Kjarni bridges this gap with a header-only wrapper that embraces contemporary C++ idioms. 

Crucially, the C++ wrapper leverages modern features like `std::expected` (introduced in C++23) for expressive, exception-free error handling:

| C++ Standard | Wrapper Support Level | Error Handling Mechanism |
| :--- | :--- | :--- |
| **C++23** | Native & Full | `std::expected<T, Error>` |
| **C++20 / C++17** | Compatible via Fallback | `std::optional` / Result structs |
| **C++11** | Compatible via Fallback | Raw status codes & pointers |

By wrapping raw C resource handles in RAII (Resource Acquisition Is Initialization) classes, the C++ interface ensures that memory and model contexts are cleaned up automatically when they fall out of scope, eliminating memory leaks without performance penalties.

## Implementing Semantic Search and Embeddings from Scratch

Let’s walk through a practical, end-to-end example of how to initialize a model, generate embeddings for a set of documents, and compute vector similarity entirely within a native C++ application.

Before running inference, ensure your model weights (typically exported in a compatible format) are accessible on disk. Here is how you set up the context and generate embeddings:

```cpp
#include "kjarni.hpp"
#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <algorithm>

// Simple cosine similarity helper
float compute_cosine_similarity(const std::vector<float>& a, const std::vector<float>& b) {
    float dot_product = 0.0f;
    float norm_a = 0.0f;
    float norm_b = 0.0f;
    
    for (size_t i = 0; i < a.size(); ++i) {
        dot_product += a[i] * b[i];
        norm_a += a[i] * a[i];
        norm_b += b[i] * b[i];
    }
    
    if (norm_a == 0.0f || norm_b == 0.0f) return 0.0f;
    return dot_product / (std::sqrt(norm_a) * std::sqrt(norm_b));
}

int main() {
    // 1. Initialize the embedding model configuration
    kjarni::ModelConfig config;
    config.model_path = "./models/minilm-l6-v2";
    config.threads = 4;

    // 2. Load the model using the C++23 wrapper (handling potential errors with std::expected)
    auto model_result = kjarni::EmbeddingModel::load(config);
    if (!model_result) {
        std::cerr << "Failed to load model: " << model_result.error().message << "\n";
        return 1;
    }
    
    // Extract the model object via RAII
    auto model = std::move(model_result.value());

    // 3. Define our corpus of text documents
    std::vector<std::string> documents = {
        "Kjarni provides a lightweight native inference engine for C++.",
        "LibTorch and ONNX Runtime introduce significant binary bloat.",
        "Semantic search enables finding documents by conceptual meaning rather than exact keywords."
    };

    // 4. Generate embeddings for the corpus
    std::vector<std::vector<float>> doc_embeddings;
    for (const auto& doc : documents) {
        auto emb_result = model.embed(doc);
        if (!emb_result) {
            std::cerr << "Embedding generation failed for: " << doc << "\n";
            continue;
        }
        doc_embeddings.push_back(std::move(emb_result.value()));
    }

    // 5. Query the index
    std::string query = "How do I run transformer models without Python?";
    auto query_emb_result = model.embed(query);
    if (!query_emb_result) {
        std::cerr << "Failed to embed query.\n";
        return 1;
    }
    auto query_embedding = std::move(query_emb_result.value());

    // 6. Compute similarity scores and rank results
    struct SearchResult {
        size_t index;
        float score;
    };
    
    std::vector<SearchResult> results;
    for (size_t i = 0; i < doc_embeddings.size(); ++i) {
        float score = compute_cosine_similarity(query_embedding, doc_embeddings[i]);
        results.push_back({i, score});
    }

    // Sort descending by similarity score
    std::sort(results.begin(), results.end(), [](const auto& a, const auto& b) {
        return a.score > b.score;
    });

    // 7. Output results
    std::cout << "Query: " << query << "\n\nTop Results:\n";
    for (const auto& res : results) {
        std::cout << "Score: " << res.score << " | Document: " << documents[res.index] << "\n";
    }

    return 0;
}
```

This snippet executes entirely within native memory space. There are no background Python threads, no IPC overhead talking to an external runtime server, and no multi-gigabyte shared object dependencies.

## Advanced Operations: Cross-Encoder Reranking

While bi-encoders (which generate independent vector embeddings for queries and documents) are fast and excel at initial retrieval stages, they sometimes miss subtle contextual nuances. If you are building a robust local Retrieval-Augmented Generation (RAG) pipeline, combining a fast bi-encoder retrieval phase with a high-precision cross-encoder reranking step is standard practice.

Understanding the fundamental trade-off helps clarify when to apply each:

| Feature | Bi-Encoder (Embeddings) | Cross-Encoder (Reranking) |
| :--- | :--- | :--- |
| **Computational Cost** | Low ($O(N)$ pre-computed vector lookups) | High ($O(N)$ real-time joint-attention scoring) |
| **Contextual Awareness** | Query and document encoded independently | Query and document processed together in one pass |
| **Primary Use Case** | Initial vector search / nearest-neighbor retrieval | Refining the top $K$ results for maximum accuracy |

To learn more about optimizing these retrieval phases, take a look at our empirical analysis on [RAG retrieval techniques and empirical performance metrics](/tech/2026/08/03/rag-retrieval-techniques-empirical-analysis.html).

With Kjarni, integrating a cross-encoder reranking pipeline into your C++ codebase follows the same lightweight pattern as the embedding model:

```cpp
// Load a cross-encoder model for reranking
kjarni::ModelConfig rerank_config;
config.model_path = "./models/ms-marco-MiniLM-L-6-v2";

auto reranker_result = kjarni::RerankerModel::load(rerank_config);
if (reranker_result) {
    auto reranker = std::move(reranker_result.value());
    
    // Score query-document pairs directly
    auto score_result = reranker.score(query, "Kjarni provides a lightweight native inference engine for C++.");
    if (score_result) {
        std::cout << "Rerank relevance score: " << score_result.value() << "\n";
    }
}
```

By decoupling the initial vector scan from the precise cross-encoder scoring, you maintain snappy response times while drastically improving the quality of the retrieved context.

## Future Outlook: The Road Ahead for Lightweight Native AI

The software landscape is shifting away from bloated, general-purpose runtimes toward specialized, lean inference engines. Developers deploying applications to edge environments, desktop plugins, or high-frequency trading systems increasingly demand software that respects system resources. 

The future trajectory for projects like Kjarni focuses on seamless ecosystem integration and expanded language accessibility:
- **Package Manager Integration:** First-class support for standard C++ package managers like Conan and vcpkg will make incorporating native transformer inference into existing CMake projects as simple as adding a single dependency line.
- **Cross-Language Ecosystems:** Because the core engine is exposed through a clean, stable C ABI, future wrappers can easily extend support to languages like C#, Go, and Python without rewriting the underlying execution code.
- **Hardware Acceleration:** Continued optimization for consumer hardware targets (such as specialized CPU instruction sets) without requiring heavy proprietary GPU driver stacks.

By embracing lightweight native design principles, you can deliver state-of-the-art semantic search and machine learning features in C++ applications that start instantly, consume minimal memory, and deploy with a single, self-contained binary.
