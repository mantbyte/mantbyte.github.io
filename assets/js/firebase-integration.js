import { observeAuthState, loginWithGoogle, logout } from './firebase/auth.js';
import { toggleLike, getLikeStatus, getPostLikes } from './firebase/likes.js';
import { castVote, getVoteStatus, getPostVotes } from './firebase/votes.js';
import { toggleBookmark, getBookmarkStatus } from './firebase/bookmarks.js';
import { addComment, getComments } from './firebase/comments.js';
import { saveReadingProgress } from './firebase/progress.js';

document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Auth State UI Updates
    const loginBtn = document.getElementById('fb-login-btn');
    const logoutBtn = document.getElementById('fb-logout-btn');
    const userAvatar = document.getElementById('fb-user-avatar');
    
    observeAuthState((user) => {
        try {
            if (user) {
                document.body.classList.add('logged-in');
                document.body.classList.remove('logged-out');
                if (userAvatar) {
                    const fallbackSvg = "data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200' viewBox='0 0 24 24' fill='%239ca3af' stroke='none'%3E%3Cpath d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z'/%3E%3C/svg%3E";
                    userAvatar.src = user.photoURL || fallbackSvg;
                    userAvatar.onerror = function() { this.src = fallbackSvg; this.onerror = null; };
                    userAvatar.title = user.displayName;
                }
                initPostInteractions(user).catch(err => {
                    console.error("Interaction init failed:", err);
                    alert("Error loading post data: " + err.message);
                });
            } else {
                document.body.classList.remove('logged-in');
                document.body.classList.add('logged-out');
            }
        } catch (err) {
            alert("Auth state error: " + err.message);
        }
    });

    if (loginBtn) {
        loginBtn.addEventListener('click', async () => {
            try { await loginWithGoogle(); } catch (e) { alert("Login failed"); }
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            await logout();
            window.location.reload();
        });
    }

    // 2. Post Interactions Initialization (only runs if on a post page)
    const postArticle = document.querySelector('article.post');
    let postSlug = '';
    
    if (postArticle) {
        // For GitHub Pages, use the full path as the slug, removing leading/trailing slashes and replacing inner slashes with hyphens
        let rawPath = window.location.pathname.replace(/^\/+|\/+$/g, '');
        postSlug = rawPath.replace(/\//g, '-');
        
        if (postSlug && postSlug !== '') {
            // Setup Reading Progress tracking
            window.addEventListener('scroll', () => {
                const docHeight = document.documentElement.scrollHeight - window.innerHeight;
                if (docHeight > 0) {
                    const scrolled = (window.scrollY / docHeight) * 100;
                    saveReadingProgress(postSlug, scrolled);
                }
            }, { passive: true });

            // Load Public Aggregates (everyone sees this)
            loadPublicCounters(postSlug);
            loadComments(postSlug);
        }
    }
    
    // Auth-dependent Interactions setup
    async function initPostInteractions(user) {
        if (!postSlug || postSlug === '') return;
        
        // Fetch personal statuses
        const [liked, voteStatus, bookmarked] = await Promise.all([
            getLikeStatus(postSlug),
            getVoteStatus(postSlug),
            getBookmarkStatus(postSlug)
        ]);
        
        updateLikeUI(liked);
        updateVoteUI(voteStatus);
        updateBookmarkUI(bookmarked);
        
        // Attach Event Listeners
        const likeBtn = document.getElementById('fb-like-btn');
        if (likeBtn) likeBtn.addEventListener('click', async () => {
            try {
                const res = await toggleLike(postSlug);
                updateLikeUI(res.liked);
                loadPublicCounters(postSlug); // refresh count
            } catch (err) { alert("Failed: " + err.message); }
        });
        
        const upvoteBtn = document.getElementById('fb-upvote-btn');
        const downvoteBtn = document.getElementById('fb-downvote-btn');
        
        if (upvoteBtn) upvoteBtn.addEventListener('click', async () => {
            try {
                const res = await castVote(postSlug, 1);
                updateVoteUI(res.vote);
                loadPublicCounters(postSlug);
            } catch (err) { alert("Failed: " + err.message); }
        });
        
        if (downvoteBtn) downvoteBtn.addEventListener('click', async () => {
            try {
                const res = await castVote(postSlug, -1);
                updateVoteUI(res.vote);
                loadPublicCounters(postSlug);
            } catch (err) { alert("Failed: " + err.message); }
        });
        
        const bookmarkBtn = document.getElementById('fb-bookmark-btn');
        if (bookmarkBtn) bookmarkBtn.addEventListener('click', async () => {
            try {
                const isBookmarked = await toggleBookmark(postSlug);
                updateBookmarkUI(isBookmarked);
            } catch (err) { alert("Failed: " + err.message); }
        });
        
        const commentForm = document.getElementById('fb-comment-form');
        if (commentForm) commentForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const input = document.getElementById('fb-comment-input');
            const content = input.value;
            if (!content) return;
            
            try {
                const newComment = await addComment(postSlug, content);
                input.value = '';
                appendCommentToUI(newComment, true);
            } catch (err) {
                alert(err.message);
            }
        });
    }
    
    async function loadPublicCounters(postSlug) {
        const likes = await getPostLikes(postSlug);
        const votes = await getPostVotes(postSlug);
        
        const likeCountEl = document.getElementById('fb-like-count');
        const voteCountEl = document.getElementById('fb-vote-count');
        
        if (likeCountEl) likeCountEl.innerText = likes;
        if (voteCountEl) voteCountEl.innerText = votes.upvotes - votes.downvotes;
    }
    
    async function loadComments(postSlug) {
        const comments = await getComments(postSlug);
        const container = document.getElementById('fb-comments-list');
        if (!container) return;
        
        container.innerHTML = '';
        if (comments.length === 0) {
            container.innerHTML = '<p class="no-comments">No comments yet. Be the first!</p>';
        } else {
            comments.forEach(c => appendCommentToUI(c, false));
        }
    }
    
    function appendCommentToUI(comment, prepend = false) {
        const container = document.getElementById('fb-comments-list');
        if (!container) return;
        
        const noComments = container.querySelector('.no-comments');
        if (noComments) noComments.remove();
        
        const el = document.createElement('div');
        el.className = 'fb-comment';
        
        const fallbackSvg = "data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200' viewBox='0 0 24 24' fill='%239ca3af' stroke='none'%3E%3Cpath d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z'/%3E%3C/svg%3E";
        const avatar = comment.authorPhoto || fallbackSvg;
        
        // Handle firestore timestamp format correctly
        let dateStr = 'Just now';
        if (comment.createdAt && typeof comment.createdAt.toDate === 'function') {
            dateStr = new Date(comment.createdAt.toDate()).toLocaleDateString();
        }
        
        el.innerHTML = `
            <img src="${avatar}" alt="Avatar" class="fb-comment-avatar">
            <div class="fb-comment-content">
                <div class="fb-comment-header">
                    <strong>${comment.authorName}</strong>
                    <span class="fb-comment-date">${dateStr}</span>
                </div>
                <div class="fb-comment-body">${comment.content}</div>
            </div>
        `;
        
        if (prepend) container.prepend(el);
        else container.appendChild(el);
    }
    
    function updateLikeUI(liked) {
        const btn = document.getElementById('fb-like-btn');
        if (!btn) return;
        if (liked) btn.classList.add('active');
        else btn.classList.remove('active');
    }
    
    function updateVoteUI(vote) {
        const up = document.getElementById('fb-upvote-btn');
        const down = document.getElementById('fb-downvote-btn');
        if (!up || !down) return;
        
        up.classList.remove('active');
        down.classList.remove('active');
        
        if (vote === 1) up.classList.add('active');
        else if (vote === -1) down.classList.add('active');
    }
    
    function updateBookmarkUI(bookmarked) {
        const btn = document.getElementById('fb-bookmark-btn');
        if (!btn) return;
        if (bookmarked) btn.classList.add('active');
        else btn.classList.remove('active');
    }
});
