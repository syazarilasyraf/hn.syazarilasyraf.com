// HN Digest - Shared JavaScript

const HN_API = 'https://hacker-news.firebaseio.com/v0';
const PREVIEW_COMMENTS_COUNT = 3;

async function fetchItem(id) {
  const res = await fetch(`${HN_API}/item/${id}.json`);
  return res.json();
}

function formatTime(timestamp) {
  const seconds = Math.floor((Date.now() / 1000) - timestamp);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
  if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
  return 'just now';
}

function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

async function fetchPreviewComments(storyId, count = 3) {
  const story = await fetchItem(storyId);
  if (!story.kids || story.kids.length === 0) return [];

  const comments = await Promise.all(
    story.kids.slice(0, count).map(async (id) => {
      const comment = await fetchItem(id);
      return comment && !comment.deleted && !comment.dead ? comment : null;
    })
  );

  return comments.filter(Boolean);
}

async function toggleStoryPreview(storyId) {
  const previewEl = document.getElementById(`preview-${storyId}`);
  
  if (previewEl.classList.contains('hidden')) {
    previewEl.classList.remove('hidden');
    previewEl.innerHTML = '<div style="text-align: center; padding: 1rem;"><span style="color: var(--text-muted);">Loading...</span></div>';
    
    try {
      const story = await fetchItem(storyId);
      const comments = await fetchPreviewComments(storyId, PREVIEW_COMMENTS_COUNT);
      
      if (comments.length === 0) {
        previewEl.innerHTML = '<p style="color: var(--text-muted);">No comments yet.</p>';
        return;
      }

      const commentsHtml = comments.map(comment => `
        <div class="preview-comment">
          <div class="preview-comment-header">
            <span class="preview-comment-author">${escapeHtml(comment.by || 'unknown')}</span>
            &middot; ${formatTime(comment.time)}
          </div>
          <div class="preview-comment-text">${comment.text || ''}</div>
        </div>
      `).join('');

      previewEl.innerHTML = `
        <div class="story-preview-header">
          <span class="story-preview-title">Top Comments</span>
          <button class="story-preview-close" onclick="toggleStoryPreview(${storyId})" aria-label="Close preview">&times;</button>
        </div>
        ${commentsHtml}
        <a href="/story/#${storyId}" class="view-full-link">View full discussion (${story.descendants || 0} comments) &rarr;</a>
      `;
    } catch (err) {
      console.error(err);
      previewEl.innerHTML = '<p style="color: var(--text-muted);">Failed to load comments. <a href="/story/#' + storyId + '">View on story page &rarr;</a></p>';
    }
  } else {
    previewEl.classList.add('hidden');
  }
}

// For story detail page - fetch and render full comments
async function fetchComments(commentIds, depth = 0) {
  if (!commentIds || commentIds.length === 0 || depth > 5) return [];
  
  const comments = await Promise.all(
    commentIds.slice(0, 20).map(async (id) => {
      const comment = await fetchItem(id);
      if (!comment || comment.deleted || comment.dead) return null;
      
      const children = comment.kids ? await fetchComments(comment.kids, depth + 1) : [];
      return { ...comment, children };
    })
  );
  
  return comments.filter(Boolean);
}

function renderComment(comment, depth = 0) {
  let html = `
    <div class="comment" id="comment-${comment.id}" style="${depth > 0 ? 'margin-left: ' + (depth * 1.5) + 'rem;' : ''}">
      <div class="comment-header">
        <span class="comment-author">${escapeHtml(comment.by || 'unknown')}</span>
        &middot; ${formatTime(comment.time)}
      </div>
      <div class="comment-text">${comment.text || ''}</div>
  `;
  
  if (comment.children && comment.children.length > 0) {
    comment.children.forEach(child => {
      html += renderComment(child, depth + 1);
    });
  }
  
  html += '</div>';
  return html;
}

async function loadStoryDetail(storyId) {
  const content = document.getElementById('story-content');
  
  try {
    const story = await fetchItem(storyId);
    
    if (!story || story.type !== 'story') {
      content.innerHTML = `
        <div class="error">
          <p>Story not found.</p>
          <p><a href="/">&larr; Back to live feed</a></p>
        </div>
      `;
      return;
    }

    const url = story.url || `https://news.ycombinator.com/item?id=${story.id}`;
    const hnUrl = `https://news.ycombinator.com/item?id=${story.id}`;
    const host = story.url 
      ? new URL(story.url).hostname.replace('www.', '') 
      : 'news.ycombinator.com';
    const timeAgo = formatTime(story.time);

    let storyHtml = `
      <article class="story-detail">
        <h2 class="story-detail-title">
          <a href="${url}" target="_blank" rel="noopener noreferrer">${escapeHtml(story.title)}</a>
        </h2>
        <div class="story-detail-meta">
          <span class="story-score">${story.score || 0} points</span>
          &middot; by ${escapeHtml(story.by || 'unknown')}
          &middot; ${timeAgo}
          &middot; ${host}
          &middot; <a href="${hnUrl}" target="_blank" rel="noopener noreferrer">view on hn</a>
        </div>
      </article>
    `;

    content.innerHTML = storyHtml + `
      <div class="status">
        <div class="spinner"></div>
        <p>Loading comments...</p>
      </div>
    `;

    if (story.kids && story.kids.length > 0) {
      const comments = await fetchComments(story.kids);
      
      let commentsHtml = `
        <section class="comments-section">
          <h3 class="comments-header">${story.descendants || comments.length} comments</h3>
      `;
      
      comments.forEach(comment => {
        commentsHtml += renderComment(comment);
      });
      
      commentsHtml += '</section>';
      
      content.innerHTML = storyHtml + commentsHtml;
    } else {
      content.innerHTML = storyHtml + `
        <section class="comments-section">
          <h3 class="comments-header">No comments</h3>
          <p style="color: var(--text-muted);">Be the first to comment on <a href="${hnUrl}" target="_blank" style="color: var(--link);">Hacker News</a>.</p>
        </section>
      `;
    }

  } catch (err) {
    console.error(err);
    content.innerHTML = `
      <div class="error">
        <p>Failed to load story. <a href=".">Retry</a></p>
        <p><a href="/">&larr; Back to live feed</a></p>
      </div>
    `;
  }
}

// For live feed page
async function loadLiveStories() {
  const content = document.getElementById('content');
  const LIMIT = 30;

  try {
    const idsRes = await fetch(`${HN_API}/topstories.json`);
    const storyIds = await idsRes.json();

    const stories = await Promise.all(
      storyIds.slice(0, LIMIT).map(async (id) => {
        const res = await fetchItem(id);
        return res;
      })
    );

    content.innerHTML = '<ol class="story-list">' + 
      stories.filter(Boolean).map((story) => {
        const url = story.url || `https://news.ycombinator.com/item?id=${story.id}`;
        const hnUrl = `https://news.ycombinator.com/item?id=${story.id}`;
        const host = story.url 
          ? new URL(story.url).hostname.replace('www.', '') 
          : 'news.ycombinator.com';
        const timeAgo = formatTime(story.time);
        const hasComments = story.descendants > 0;
        
        return `
          <li class="story" id="story-${story.id}">
            <div class="story-header">
              <h2 class="story-title">
                <a href="${url}" target="_blank" rel="noopener noreferrer">${escapeHtml(story.title)}</a>
              </h2>
              <div class="story-meta">
                <span class="story-score">${story.score} points</span>
                &middot; by ${escapeHtml(story.by)}
                &middot; ${timeAgo}
                &middot; ${host}
                ${hasComments ? `&middot; <button class="story-expand" onclick="toggleStoryPreview(${story.id})">${story.descendants} comments</button>` : ''}
                &middot; <a href="${hnUrl}" target="_blank">hn</a>
              </div>
            </div>
            <div class="story-preview hidden" id="preview-${story.id}"></div>
          </li>
        `;
      }).join('') + 
    '</ol>';

  } catch (err) {
    console.error(err);
    content.innerHTML = '<div class="status">Failed to load stories. <a href=".">Retry</a></div>';
  }
}

// Subscribe form handler - Buttondown API
function initSubscribeForm() {
  const form = document.getElementById('subscribe-form');
  if (!form) return;
  
  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    const btn = document.getElementById('subscribe-btn');
    const emailInput = document.getElementById('email');
    const email = emailInput.value.trim();
    
    if (!email) {
      alert('Please enter an email address');
      return;
    }
    
    btn.textContent = 'Subscribing...';
    btn.disabled = true;
    
    try {
      const response = await fetch('https://api.buttondown.email/v1/subscribers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Token 7e746bb6-e372-44f8-bc9f-a919a4fb1601'
        },
        body: JSON.stringify({
          email_address: email,
          tags: ['website']
        })
      });
      
      if (response.ok) {
        btn.textContent = 'Subscribed!';
        emailInput.value = '';
        setTimeout(() => {
          btn.textContent = 'Subscribe';
        }, 3000);
      } else if (response.status === 409) {
        // 409 = already subscribed
        btn.textContent = 'Already subscribed!';
        setTimeout(() => {
          btn.textContent = 'Subscribe';
        }, 3000);
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('Buttondown error:', response.status, errorData);
        
        // Handle specific error messages
        if (errorData.code === 'subscriber_suppressed') {
          alert('This email was previously unsubscribed. Please contact support to resubscribe.');
        } else if (errorData.detail) {
          alert('Error: ' + errorData.detail);
        } else {
          alert('Failed to subscribe. Please try again.');
        }
        btn.textContent = 'Subscribe';
      }
    } catch (err) {
      console.error('Network error:', err);
      alert('Network error. Please try again.');
      btn.textContent = 'Subscribe';
    }
    
    btn.disabled = false;
  });
}
