<template>
  <div class="page">
    <section class="hero">
      <div class="hero-main">
        <div class="pill">AI Book Narration Studio</div>

        <h1>Transform PDFs into polished narration and audio</h1>

        <p class="subtitle">
          Upload a book PDF, select a page range or chapter, and generate a clear narration script with playable audio.
          Designed for fast reading, deep reading, history tracking, and favorite task management.
        </p>

        <div class="hero-actions">
          <RouterLink class="primary-action" to="/book-narrator">
            Create Narration
          </RouterLink>

          <RouterLink class="secondary-action" to="/narration-history">
            View History
          </RouterLink>

          <RouterLink class="secondary-action" to="/favorites">
            Favorites
          </RouterLink>
        </div>
      </div>

      <div class="hero-dashboard">
        <div class="dashboard-card active">
          <span class="dashboard-label">Workflow</span>
          <h3>3-step narration pipeline</h3>
          <p>Upload PDF → configure section → generate script and audio.</p>
        </div>

        <div class="mini-grid">
          <div class="mini-card">
            <span>PDF</span>
            <strong>Source-based</strong>
          </div>

          <div class="mini-card">
            <span>AI</span>
            <strong>Script generation</strong>
          </div>

          <div class="mini-card">
            <span>MP3</span>
            <strong>Audio output</strong>
          </div>

          <div class="mini-card">
            <span>LOG</span>
            <strong>Task history</strong>
          </div>
        </div>
      </div>
    </section>

    <section class="feature-grid">
      <article class="feature-card">
        <div class="feature-top">
          <span class="step">01</span>
          <span class="tag">Upload</span>
        </div>
        <h2>Choose a PDF book</h2>
        <p>
          Upload a new PDF or select an existing file from the shared backend directory.
        </p>
      </article>

      <article class="feature-card">
        <div class="feature-top">
          <span class="step">02</span>
          <span class="tag">Configure</span>
        </div>
        <h2>Set narration options</h2>
        <p>
          Choose page range, chapter, custom text, reading mode, narration style, and voice.
        </p>
      </article>

      <article class="feature-card">
        <div class="feature-top">
          <span class="step">03</span>
          <span class="tag">Generate</span>
        </div>
        <h2>Create script and audio</h2>
        <p>
          Run background tasks, restore progress after refresh, and review results from history.
        </p>
      </article>
    </section>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 42px;
  background:
    radial-gradient(circle at 8% 0%, rgba(79, 70, 229, 0.18), transparent 32%),
    radial-gradient(circle at 92% 10%, rgba(14, 165, 233, 0.16), transparent 34%),
    linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
  color: #0f172a;
}

.hero {
  max-width: 1220px;
  margin: 0 auto 22px;
  padding: 48px;
  border-radius: 36px;
  color: white;
  background:
    linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(30, 41, 59, 0.96)),
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.36), transparent 40%);
  display: grid;
  grid-template-columns: 1.25fr 0.85fr;
  gap: 34px;
  box-shadow: 0 34px 90px rgba(15, 23, 42, 0.28);
  position: relative;
  overflow: hidden;
}

.hero::after {
  content: "";
  position: absolute;
  right: -100px;
  top: -120px;
  width: 330px;
  height: 330px;
  border-radius: 999px;
  background: rgba(96, 165, 250, 0.18);
}

.hero-main,
.hero-dashboard {
  position: relative;
  z-index: 1;
}

.pill {
  display: inline-flex;
  padding: 8px 13px;
  border-radius: 999px;
  color: #bfdbfe;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.16);
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.hero h1 {
  margin: 22px 0 0;
  max-width: 760px;
  font-size: 58px;
  line-height: 1.02;
  letter-spacing: -0.055em;
}

.subtitle {
  margin-top: 22px;
  max-width: 720px;
  color: #cbd5e1;
  font-size: 18px;
  line-height: 1.85;
}

.hero-actions {
  display: flex;
  gap: 12px;
  margin-top: 34px;
  flex-wrap: wrap;
}

.primary-action,
.secondary-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 13px 20px;
  border-radius: 999px;
  text-decoration: none;
  font-weight: 900;
  transition: transform 0.16s ease, box-shadow 0.16s ease;
}

.primary-action {
  color: #0f172a;
  background: white;
  box-shadow: 0 15px 36px rgba(255, 255, 255, 0.18);
}

.secondary-action {
  color: white;
  background: rgba(255, 255, 255, 0.13);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.primary-action:hover,
.secondary-action:hover {
  transform: translateY(-2px);
}

.hero-dashboard {
  display: grid;
  align-content: center;
  gap: 16px;
}

.dashboard-card {
  padding: 24px;
  border-radius: 26px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.16);
  backdrop-filter: blur(16px);
}

.dashboard-label {
  color: #93c5fd;
  font-size: 13px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.dashboard-card h3 {
  margin: 14px 0 8px;
  font-size: 24px;
  letter-spacing: -0.03em;
}

.dashboard-card p {
  margin: 0;
  color: #cbd5e1;
  line-height: 1.75;
}

.mini-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.mini-card {
  padding: 16px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.105);
  border: 1px solid rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(14px);
}

.mini-card span {
  display: block;
  color: #93c5fd;
  font-size: 12px;
  font-weight: 900;
  margin-bottom: 8px;
}

.mini-card strong {
  color: white;
  font-size: 14px;
}

.feature-grid {
  max-width: 1220px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.feature-card {
  padding: 26px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(226, 232, 240, 0.92);
  box-shadow: 0 20px 52px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(12px);
  transition: transform 0.16s ease, box-shadow 0.16s ease;
}

.feature-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 28px 70px rgba(15, 23, 42, 0.13);
}

.feature-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.step {
  width: 48px;
  height: 48px;
  display: grid;
  place-items: center;
  border-radius: 17px;
  background: #eef2ff;
  color: #4f46e5;
  font-weight: 900;
}

.tag {
  padding: 7px 11px;
  border-radius: 999px;
  background: #f1f5f9;
  color: #475569;
  font-size: 13px;
  font-weight: 900;
}

.feature-card h2 {
  margin: 22px 0 10px;
  letter-spacing: -0.025em;
}

.feature-card p {
  margin: 0;
  color: #64748b;
  line-height: 1.85;
}

@media (max-width: 980px) {
  .page {
    padding: 22px;
  }

  .hero {
    grid-template-columns: 1fr;
    padding: 34px;
  }

  .hero h1 {
    font-size: 40px;
  }

  .feature-grid {
    grid-template-columns: 1fr;
  }
}
</style>
