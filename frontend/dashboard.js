async function fetchText(path) {
  const res = await fetch(path);
  return res.text();
}

async function loadDashboard() {
  try {
    const [fingerprints, provenance, decisions] = await Promise.all([
      fetchText('/provenance/checksum_history.json').catch(() => '[]'),
      fetchText('/provenance/provenance_log.json').catch(() => '[]'),
      fetchText('/logs/training_audit.log').catch(() => ''),
    ]);

    document.getElementById('fingerprints').innerText = fingerprints;
    document.getElementById('provenance').innerText = provenance;
    document.getElementById('decisions').innerText = decisions || 'No decisions yet';
    document.getElementById('score-timeline').innerText = 'Scores are generated after calling /tdie_score';
  } catch (err) {
    document.getElementById('fingerprints').innerText = 'Unable to load dashboard data';
    console.error(err);
  }
}

document.addEventListener('DOMContentLoaded', loadDashboard);
