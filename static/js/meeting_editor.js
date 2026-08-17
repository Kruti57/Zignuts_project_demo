/**
 * Meeting Editor & AI Insights Engine
 * Manages Quill editor, TXT file drag/drop, AI processing workflow, and Action Extraction.
 */

// Sample Demo Transcripts for rapid evaluation
const SAMPLE_TRANSCRIPTS = {
  sprint: `Zignuts AI Platform Architecture & Sprint Deliverables Review
Date: August 17, 2026
Attendees: Sarah Connor (Tech Lead), David Kim (Backend Lead), Elena Rostova (Frontend Lead), Michael Chen (Product Manager)

Sarah Connor (Tech Lead): Welcome everyone. Our main goal for this sprint is closing the customer onboarding bottleneck and finalizing the AI Meeting Notes integration.
David Kim (Backend Lead): On the backend architecture, Sarah and I reviewed the schema. We decided to use MySQL with PyMySQL connection pooling for high throughput. I will finalize the database migration scripts and set up the DRF endpoints by Friday.
Elena Rostova (Frontend Lead): On the frontend, I am building the modern SaaS dashboard and the Action Tracker. I will complete the Quill rich text editor and the dark mode theme by Thursday.
Michael Chen (Product Manager): Great. Sarah, what about the AI service fallback?
Sarah Connor: We agreed that if the Gemini API key is missing or rate limited, the system must seamlessly fall back to an intelligent structured mock AI without throwing errors. I will write the AI client wrapper and validation tests by tomorrow.
David Kim: One concern: what if the external webhook experiences latency during action item sync?
Sarah Connor: That is a potential risk. We should add retry logic and timeout limits.
Elena Rostova: Michael, do we need multi-language transcript support in this phase?
Michael Chen: That is an open question. Let's verify customer demand before scoping it for next quarter.

Action Items:
- David Kim: Finalize database migrations and DRF endpoints by Friday (Priority: High)
- Elena Rostova: Build modern SaaS dashboard and action tracker UI by Thursday (Priority: High)
- Sarah Connor: Implement AI client wrapper and mock fallback validation by tomorrow (Priority: High)
- Michael Chen: Check customer demand for multi-language transcript support by next week (Priority: Medium)
`,
};

document.addEventListener('DOMContentLoaded', () => {
  // 1. Initialize Quill Editor if container exists
  const editorContainer = document.getElementById('quill-editor');
  const hiddenInput = document.getElementById('meeting-transcript-hidden');
  let quill = null;

  if (editorContainer && hiddenInput) {
    quill = new Quill('#quill-editor', {
      theme: 'snow',
      placeholder: 'Enter or paste meeting transcript here, or drag & drop a .txt file...',
      modules: {
        toolbar: [
          [{ 'header': [1, 2, 3, false] }],
          ['bold', 'italic', 'underline', 'strike'],
          [{ 'list': 'ordered'}, { 'list': 'bullet' }],
          ['blockquote', 'code-block'],
          ['clean']
        ]
      }
    });

    // Populate existing transcript
    if (hiddenInput.value) {
      quill.root.innerHTML = hiddenInput.value;
      updateWordCount(quill.getText());
    }

    // Sync on text change
    quill.on('text-change', () => {
      hiddenInput.value = quill.root.innerHTML;
      updateWordCount(quill.getText());
    });

    // Form submit listener to ensure synced value
    const meetingForm = document.getElementById('meeting-form');
    if (meetingForm) {
      meetingForm.addEventListener('submit', () => {
        hiddenInput.value = quill.root.innerHTML;
      });
    }
  }

  // 2. Drag & Drop / File Input Handling
  const dropzone = document.getElementById('upload-dropzone');
  const fileInput = document.getElementById('txt-file-input');

  if (dropzone && fileInput) {
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('dragover');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('dragover');
      }, false);
    });

    dropzone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files.length > 0) {
        handleTxtFile(files[0]);
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        handleTxtFile(e.target.files[0]);
      }
    });
  }

  function handleTxtFile(file) {
    if (!file.name.toLowerCase().endsWith('.txt')) {
      showToast('Please upload a valid .txt text file.', 'danger');
      return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
      const textContent = e.target.result;
      if (quill) {
        quill.setText(textContent);
        if (hiddenInput) hiddenInput.value = quill.root.innerHTML;
        updateWordCount(textContent);
      }
      showToast(`Loaded ${file.name} successfully!`, 'success');
    };
    reader.readAsText(file);
  }

  // 3. Insert Sample Demo Transcript Buttons
  document.querySelectorAll('.insert-sample-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const sampleKey = btn.getAttribute('data-sample') || 'sprint';
      const sampleText = SAMPLE_TRANSCRIPTS[sampleKey] || SAMPLE_TRANSCRIPTS.sprint;

      if (quill) {
        quill.setText(sampleText);
        if (hiddenInput) hiddenInput.value = quill.root.innerHTML;
        updateWordCount(sampleText);
        showToast(`Loaded ${sampleKey} sample transcript!`, 'info');
      }
    });
  });

  function updateWordCount(text) {
    const wordCountEl = document.getElementById('editor-word-count');
    const charCountEl = document.getElementById('editor-char-count');
    if (!wordCountEl || !charCountEl) return;

    const trimmed = text.trim();
    const words = trimmed ? trimmed.split(/\s+/).length : 0;
    const chars = trimmed.length;

    wordCountEl.textContent = `${words} words`;
    charCountEl.textContent = `${chars} chars`;
  }

  // 4. AI Insights Generation on Meeting Detail Page
  const generateAiBtn = document.getElementById('btn-generate-ai');
  if (generateAiBtn) {
    generateAiBtn.addEventListener('click', () => {
      const meetingId = generateAiBtn.getAttribute('data-meeting-id');
      if (!meetingId) return;

      startAiGeneration(meetingId);
    });
  }

  function startAiGeneration(meetingId) {
    const loadingState = document.getElementById('ai-loading-state');
    const emptyState = document.getElementById('ai-empty-state');
    const resultsContainer = document.getElementById('ai-results-container');
    const generateBtn = document.getElementById('btn-generate-ai');

    if (emptyState) emptyState.classList.add('d-none');
    if (resultsContainer) resultsContainer.classList.add('d-none');
    if (loadingState) loadingState.classList.remove('d-none');
    if (generateBtn) generateBtn.disabled = true;

    // Animate loading steps
    const step1 = document.getElementById('ai-step-1');
    const step2 = document.getElementById('ai-step-2');
    const step3 = document.getElementById('ai-step-3');
    const step4 = document.getElementById('ai-step-4');

    setTimeout(() => { if (step1) step1.className = 'd-flex align-items-center gap-2 text-primary fw-semibold'; }, 200);
    setTimeout(() => { if (step2) step2.className = 'd-flex align-items-center gap-2 text-primary fw-semibold'; }, 800);
    setTimeout(() => { if (step3) step3.className = 'd-flex align-items-center gap-2 text-primary fw-semibold'; }, 1400);
    setTimeout(() => { if (step4) step4.className = 'd-flex align-items-center gap-2 text-primary fw-semibold'; }, 1800);

    fetch('/api/ai/generate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({ meeting_id: parseInt(meetingId, 10) })
    })
    .then(res => {
      if (!res.ok) throw new Error('AI generation failed with status ' + res.status);
      return res.json();
    })
    .then(data => {
      if (loadingState) loadingState.classList.add('d-none');
      if (generateBtn) generateBtn.disabled = false;

      if (data.success && data.insights) {
        renderAiInsights(data.insights, data.provider);
        showToast(`AI Insights generated using ${data.provider.toUpperCase()} provider!`, 'success');
      } else {
        throw new Error(data.error || 'Failed to parse AI insights');
      }
    })
    .catch(err => {
      if (loadingState) loadingState.classList.add('d-none');
      if (emptyState) emptyState.classList.remove('d-none');
      if (generateBtn) generateBtn.disabled = false;
      showToast('Error generating AI Insights: ' + err.message, 'danger');
    });
  }

  function renderAiInsights(insights, provider) {
    const resultsContainer = document.getElementById('ai-results-container');
    if (!resultsContainer) return;

    // 1. Provider Badge & Summary
    const summaryText = document.getElementById('insight-summary-text');
    const providerBadge = document.getElementById('ai-provider-badge');
    if (summaryText) summaryText.textContent = insights.summary || 'No summary available.';
    if (providerBadge) {
      providerBadge.textContent = (provider || 'AI').toUpperCase();
      providerBadge.className = 'badge bg-primary-subtle text-primary border border-primary-subtle';
    }

    // 2. Key Decisions
    const decisionsList = document.getElementById('insight-decisions-list');
    if (decisionsList) {
      decisionsList.innerHTML = '';
      (insights.key_decisions || []).forEach(dec => {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex align-items-start gap-2 bg-transparent';
        li.innerHTML = `<i class="bi bi-check-circle-fill text-success mt-1"></i> <div>${escapeHtml(dec)}</div>`;
        decisionsList.appendChild(li);
      });
    }

    // 3. Discussion Points
    const discussionList = document.getElementById('insight-discussion-list');
    if (discussionList) {
      discussionList.innerHTML = '';
      (insights.discussion_points || []).forEach(dp => {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex align-items-start gap-2 bg-transparent';
        li.innerHTML = `<i class="bi bi-chat-left-quote text-primary mt-1"></i> <div>${escapeHtml(dp)}</div>`;
        discussionList.appendChild(li);
      });
    }

    // 4. Risks & Concerns
    const risksList = document.getElementById('insight-risks-list');
    if (risksList) {
      risksList.innerHTML = '';
      (insights.risks_and_concerns || []).forEach(risk => {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex align-items-start gap-2 bg-transparent';
        li.innerHTML = `<i class="bi bi-exclamation-triangle-fill text-warning mt-1"></i> <div>${escapeHtml(risk)}</div>`;
        risksList.appendChild(li);
      });
    }

    // 5. Unanswered Questions
    const questionsList = document.getElementById('insight-questions-list');
    if (questionsList) {
      questionsList.innerHTML = '';
      (insights.unanswered_questions || []).forEach(q => {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex align-items-start gap-2 bg-transparent';
        li.innerHTML = `<i class="bi bi-question-circle-fill text-info mt-1"></i> <div>${escapeHtml(q)}</div>`;
        questionsList.appendChild(li);
      });
    }

    // 6. Action Items Table / List
    const actionsTableBody = document.getElementById('insight-actions-table-body');
    if (actionsTableBody) {
      actionsTableBody.innerHTML = '';
      window.__latestAiActions = insights.action_items || [];

      (insights.action_items || []).forEach((act, idx) => {
        const tr = document.createElement('tr');
        const priorityBadge = act.priority === 'HIGH' ? 'bg-danger-subtle text-danger' :
                              act.priority === 'LOW' ? 'bg-info-subtle text-info' : 'bg-warning-subtle text-warning-emphasis';

        tr.innerHTML = `
          <td>
            <div class="fw-medium">${escapeHtml(act.task)}</div>
          </td>
          <td>
            <span class="badge bg-secondary-subtle text-secondary"><i class="bi bi-person me-1"></i>${escapeHtml(act.owner || 'Unassigned')}</span>
          </td>
          <td>
            <span class="small text-muted"><i class="bi bi-calendar3 me-1"></i>${escapeHtml(act.due_date || 'Not specified')}</span>
          </td>
          <td>
            <span class="badge ${priorityBadge}">${escapeHtml(act.priority)}</span>
          </td>
          <td class="text-end">
            <button class="btn btn-sm btn-outline-primary extract-single-action-btn" data-action-index="${idx}">
              <i class="bi bi-plus-circle me-1"></i> Save
            </button>
          </td>
        `;
        actionsTableBody.appendChild(tr);
      });

      // Attach single extract listeners
      document.querySelectorAll('.extract-single-action-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const idx = parseInt(btn.getAttribute('data-action-index'), 10);
          const actItem = window.__latestAiActions[idx];
          if (actItem) {
            extractActions([actItem], btn);
          }
        });
      });
    }

    resultsContainer.classList.remove('d-none');
    resultsContainer.classList.add('animate-fade-up');
  }

  // Bind single extract listeners to pre-rendered elements on page load
  document.querySelectorAll('.extract-single-action-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const idx = parseInt(btn.getAttribute('data-action-index'), 10);
      const actItem = window.__latestAiActions && window.__latestAiActions[idx];
      if (actItem) {
        extractActions([actItem], btn);
      }
    });
  });

  // 5. Bulk Extract Action Items to Database
  const extractAllBtn = document.getElementById('btn-extract-all-actions');
  if (extractAllBtn) {
    extractAllBtn.addEventListener('click', () => {
      const meetingId = extractAllBtn.getAttribute('data-meeting-id');
      if (window.__latestAiActions && window.__latestAiActions.length > 0) {
        extractActions(window.__latestAiActions, extractAllBtn, meetingId);
      } else {
        showToast('No action items available to extract.', 'warning');
      }
    });
  }

  function extractActions(actionItemsList, buttonEl, meetingIdParam) {
    const meetingId = meetingIdParam || (document.getElementById('btn-generate-ai') ? document.getElementById('btn-generate-ai').getAttribute('data-meeting-id') : null);

    if (buttonEl) {
      buttonEl.disabled = true;
      buttonEl.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Saving...';
    }

    fetch('/api/ai/extract-actions/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({
        meeting_id: meetingId ? parseInt(meetingId, 10) : null,
        action_items: actionItemsList
      })
    })
    .then(res => {
      if (!res.ok) throw new Error('Failed to extract action items');
      return res.json();
    })
    .then(data => {
      showToast(`Successfully extracted ${data.count} action item(s) to the Action Tracker!`, 'success');
      if (buttonEl) {
        buttonEl.innerHTML = '<i class="bi bi-check2-circle me-1"></i> Saved';
        buttonEl.classList.remove('btn-outline-primary');
        buttonEl.classList.add('btn-success');
      }
      setTimeout(() => {
        window.location.reload();
      }, 1200);
    })
    .catch(err => {
      showToast('Error saving action items: ' + err.message, 'danger');
      if (buttonEl) {
        buttonEl.disabled = false;
        buttonEl.innerHTML = '<i class="bi bi-arrow-clockwise me-1"></i> Retry';
      }
    });
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});
