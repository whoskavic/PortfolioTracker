import { useQuery } from '@tanstack/react-query'
import { TrendingUp, TrendingDown, DollarSign, Layers } from 'lucide-react'
import Layout from '../components/Layout'
import client from '../api/client'
import { formatUSD, pnlColor, pnlSign } from '../utils/format'

function SummaryCard({ title, value, subtitle, icon: Icon, iconColor }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-slate-400">{title}</span>
        <Icon className={`w-4 h-4 ${iconColor}`} />
      </div>
      <div className="text-xl font-semibold text-white">{value}</div>
      {subtitle && <div className="text-xs text-slate-500 mt-1">{subtitle}</div>}
    </div>
  )
}

function PnlPeriodCard({ label, data }) {
  const pnl = data?.total_pnl ?? 0
  const pct = data?.total_pnl_percentage ?? 0
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
      <div className="text-xs text-slate-400 mb-2">{label}</div>
      <div className={`text-lg font-semibold ${pnlColor(pnl)}`}>
        {pnlSign(pnl)}{formatUSD(pnl)}
      </div>
      <div className={`text-xs mt-0.5 ${pnlColor(pct)}`}>
        {pnlSign(pct)}{pct.toFixed(2)}%
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['portfolio-summary'],
    queryFn: () => client.get('/portfolio/summary').then(r => r.data),
  })

  const { data: positions = [], isLoading: posLoading } = useQuery({
    queryKey: ['positions'],
    queryFn: () => client.get('/positions').then(r => r.data),
  })

  return (
    <Layout>
      <div className="p-6 space-y-6">
        <h1 className="text-lg font-semibold text-white">Dashboard</h1>

        {/* Summary Cards */}
        {summaryLoading ? (
          <div className="text-slate-400 text-sm">Loading summary...</div>
        ) : (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <SummaryCard
              title="Total Invested"
              value={formatUSD(summary?.total_invested)}
              icon={DollarSign}
              iconColor="text-blue-400"
            />
            <SummaryCard
              title="Current Value"
              value={formatUSD(summary?.current_value)}
              icon={Layers}
              iconColor="text-purple-400"
            />
            <SummaryCard
              title="Total PnL"
              value={
                <span className={pnlColor(summary?.total_pnl)}>
                  {pnlSign(summary?.total_pnl)}{formatUSD(summary?.total_pnl)}
                </span>
              }
              subtitle={`${pnlSign(summary?.total_pnl_percentage)}${(summary?.total_pnl_percentage ?? 0).toFixed(2)}%`}
              icon={(summary?.total_pnl ?? 0) >= 0 ? TrendingUp : TrendingDown}
              iconColor={(summary?.total_pnl ?? 0) >= 0 ? 'text-emerald-400' : 'text-red-400'}
            />
            <SummaryCard
              title="Positions"
              value={summary?.total_positions ?? 0}
              subtitle={`${summary?.total_transactions ?? 0} transactions`}
              icon={Layers}
              iconColor="text-slate-400"
            />
          </div>
        )}

        {/* PnL by Period */}
        {!summaryLoading && (
          <div>
            <h2 className="text-sm font-medium text-slate-400 mb-3">PnL by Period</h2>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <PnlPeriodCard label="7 Days" data={summary?.pnl_7d} />
              <PnlPeriodCard label="30 Days" data={summary?.pnl_30d} />
              <PnlPeriodCard label="1 Year" data={summary?.pnl_1y} />
              <PnlPeriodCard label="All Time" data={summary?.pnl_all} />
            </div>
          </div>
        )}

        {/* Positions Table */}
        <div>
          <h2 className="text-sm font-medium text-slate-400 mb-3">Current Positions</h2>
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
            {posLoading ? (
              <div className="p-6 text-center text-slate-400 text-sm">Loading...</div>
            ) : positions.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-sm">No positions yet</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-800">
                      <th className="text-left px-4 py-3 text-xs font-medium text-slate-400">Asset</th>
                      <th className="text-right px-4 py-3 text-xs font-medium text-slate-400">Qty</th>
                      <th className="text-right px-4 py-3 text-xs font-medium text-slate-400">Avg Buy</th>
                      <th className="text-right px-4 py-3 text-xs font-medium text-slate-400">Invested</th>
                      <th className="text-right px-4 py-3 text-xs font-medium text-slate-400">Unrealized PnL</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {positions.map(pos => (
                      <tr key={pos.id} className="hover:bg-slate-800/40">
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-white">{pos.asset.symbol}</span>
                            <span className="text-slate-500 text-xs">{pos.asset.name}</span>
                            <span className={`text-xs px-1.5 py-0.5 rounded ${
                              pos.asset.asset_type === 'crypto'
                                ? 'bg-orange-500/10 text-orange-400'
                                : 'bg-blue-500/10 text-blue-400'
                            }`}>
                              {pos.asset.asset_type}
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-right text-white font-mono text-xs">{pos.quantity}</td>
                        <td className="px-4 py-3 text-right text-slate-300 text-xs">{formatUSD(pos.average_buy_price)}</td>
                        <td className="px-4 py-3 text-right text-slate-300 text-xs">{formatUSD(pos.total_invested)}</td>
                        <td className={`px-4 py-3 text-right text-xs ${pnlColor(pos.unrealized_pnl)}`}>
                          {pos.unrealized_pnl !== 0 ? `${pnlSign(pos.unrealized_pnl)}${formatUSD(pos.unrealized_pnl)}` : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}
