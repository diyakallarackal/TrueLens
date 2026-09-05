export const formatBytes = (bytes, decimals = 2) => {
  if (!bytes || bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

export const getVerdictColor = (verdict, riskScore) => {
  if (verdict === 'Likely Authentic' || riskScore < 35) {
    return {
      badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      text: 'text-emerald-400',
      border: 'border-emerald-500/40',
      bg: 'bg-emerald-500/5',
      accent: '#10b981',
    };
  }
  if (verdict === 'Inconclusive' || (riskScore >= 35 && riskScore < 65)) {
    return {
      badge: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      text: 'text-amber-400',
      border: 'border-amber-500/40',
      bg: 'bg-amber-500/5',
      accent: '#f59e0b',
    };
  }
  return {
    badge: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
    text: 'text-rose-400',
    border: 'border-rose-500/40',
    bg: 'bg-rose-500/5',
    accent: '#f43f5e',
  };
};

export const getSeverityBadge = (severity) => {
  switch (severity?.toLowerCase()) {
    case 'high':
    case 'critical':
      return 'bg-rose-500/15 text-rose-400 border-rose-500/30';
    case 'medium':
      return 'bg-amber-500/15 text-amber-400 border-amber-500/30';
    default:
      return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
  }
};

export const formatDate = (isoString) => {
  if (!isoString) return '';
  try {
    const d = new Date(isoString);
    return d.toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch (e) {
    return isoString;
  }
};
