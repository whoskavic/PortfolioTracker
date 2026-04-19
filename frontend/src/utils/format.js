export const formatUSD = (n) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n ?? 0)

export const formatIDR = (n) =>
  new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(n ?? 0)

export const formatCurrency = (n, currency = 'USD') =>
  currency === 'IDR' ? formatIDR(n) : formatUSD(n)

export const formatNumber = (n, decimals = 8) =>
  Number(n ?? 0).toLocaleString('en-US', { maximumFractionDigits: decimals })

export const pnlColor = (n) =>
  n > 0 ? 'text-emerald-400' : n < 0 ? 'text-red-400' : 'text-slate-400'

export const pnlSign = (n) => (n > 0 ? '+' : '')

export const formatDate = (d) =>
  new Date(d).toLocaleString('id-ID', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
