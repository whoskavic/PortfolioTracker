import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2, X } from 'lucide-react'
import Layout from '../components/Layout'
import client from '../api/client'
import { formatCurrency, formatUSD, formatDate, pnlColor, pnlSign } from '../utils/format'

function AddAssetModal({ onClose, onCreated }) {
  const [form, setForm] = useState({ symbol: '', name: '', asset_type: 'crypto' })
  const [error, setError] = useState('')
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: (data) => client.post('/assets', data).then(r => r.data),
    onSuccess: (asset) => {
      queryClient.invalidateQueries(['assets'])
      onCreated(asset)
      onClose()
    },
    onError: (err) => setError(err.response?.data?.detail || 'Failed to create asset'),
  })

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 px-4">
      <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-sm p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-white">Add Asset</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-3">
          <div>
            <label className="block text-xs text-slate-400 mb-1">Symbol</label>
            <input
              value={form.symbol}
              onChange={e => setForm(p => ({ ...p, symbol: e.target.value.toUpperCase() }))}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              placeholder="BTC"
            />
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">Name</label>
            <input
              value={form.name}
              onChange={e => setForm(p => ({ ...p, name: e.target.value }))}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              placeholder="Bitcoin"
            />
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">Type</label>
            <select
              value={form.asset_type}
              onChange={e => setForm(p => ({ ...p, asset_type: e.target.value }))}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
            >
              <option value="crypto">Crypto</option>
              <option value="stock">Stock</option>
            </select>
          </div>
          {error && <p className="text-red-400 text-xs">{error}</p>}
          <button
            onClick={() => mutation.mutate(form)}
            disabled={mutation.isPending}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium py-2 rounded-lg transition-colors"
          >
            {mutation.isPending ? 'Creating...' : 'Create Asset'}
          </button>
        </div>
      </div>
    </div>
  )
}

function AddTransactionModal({ onClose }) {
  const queryClient = useQueryClient()
  const [showAddAsset, setShowAddAsset] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    asset_id: '',
    transaction_type: 'buy',
    quantity: '',
    price: '',
    fee: '0',
    currency: 'USD',
    transaction_date: new Date().toISOString().slice(0, 16),
    notes: '',
  })

  const { data: assets = [] } = useQuery({
    queryKey: ['assets'],
    queryFn: () => client.get('/assets').then(r => r.data),
  })

  const mutation = useMutation({
    mutationFn: (data) => client.post('/transactions', data).then(r => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries(['transactions'])
      queryClient.invalidateQueries(['positions'])
      queryClient.invalidateQueries(['portfolio-summary'])
      onClose()
    },
    onError: (err) => setError(err.response?.data?.detail || 'Failed to create transaction'),
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')
    mutation.mutate({
      ...form,
      asset_id: Number(form.asset_id),
      quantity: Number(form.quantity),
      price: Number(form.price),
      fee: Number(form.fee),
      transaction_date: form.transaction_date + ':00',
    })
  }

  return (
    <>
      {showAddAsset && (
        <AddAssetModal
          onClose={() => setShowAddAsset(false)}
          onCreated={(asset) => setForm(p => ({ ...p, asset_id: String(asset.id) }))}
        />
      )}
      <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-40 px-4">
        <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-md p-5 max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Add Transaction</h3>
            <button onClick={onClose} className="text-slate-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs text-slate-400">Asset</label>
                <button
                  type="button"
                  onClick={() => setShowAddAsset(true)}
                  className="text-xs text-blue-400 hover:text-blue-300"
                >
                  + New Asset
                </button>
              </div>
              <select
                value={form.asset_id}
                onChange={e => setForm(p => ({ ...p, asset_id: e.target.value }))}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                required
              >
                <option value="">Select asset...</option>
                {assets.map(a => (
                  <option key={a.id} value={a.id}>{a.symbol} — {a.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">Type</label>
              <div className="flex gap-2">
                {['buy', 'sell'].map(t => (
                  <button
                    key={t}
                    type="button"
                    onClick={() => setForm(p => ({ ...p, transaction_type: t }))}
                    className={`flex-1 py-2 rounded-lg text-sm font-medium capitalize transition-colors ${
                      form.transaction_type === t
                        ? t === 'buy' ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white'
                        : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-slate-400 mb-1">Quantity</label>
                <input
                  type="number" step="any" min="0"
                  value={form.quantity}
                  onChange={e => setForm(p => ({ ...p, quantity: e.target.value }))}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                  placeholder="0.00"
                  required
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Price per unit</label>
                <input
                  type="number" step="any" min="0"
                  value={form.price}
                  onChange={e => setForm(p => ({ ...p, price: e.target.value }))}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                  placeholder="0.00"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-slate-400 mb-1">Fee</label>
                <input
                  type="number" step="any" min="0"
                  value={form.fee}
                  onChange={e => setForm(p => ({ ...p, fee: e.target.value }))}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                  placeholder="0"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Currency</label>
                <select
                  value={form.currency}
                  onChange={e => setForm(p => ({ ...p, currency: e.target.value }))}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="USD">USD</option>
                  <option value="IDR">IDR</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">Date & Time</label>
              <input
                type="datetime-local"
                value={form.transaction_date}
                onChange={e => setForm(p => ({ ...p, transaction_date: e.target.value }))}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">Notes (optional)</label>
              <input
                type="text"
                value={form.notes}
                onChange={e => setForm(p => ({ ...p, notes: e.target.value }))}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                placeholder="Optional note..."
              />
            </div>

            {error && <p className="text-red-400 text-xs">{error}</p>}

            <button
              type="submit"
              disabled={mutation.isPending}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium py-2 rounded-lg transition-colors"
            >
              {mutation.isPending ? 'Adding...' : 'Add Transaction'}
            </button>
          </form>
        </div>
      </div>
    </>
  )
}

export default function TransactionsPage() {
  const [showAddModal, setShowAddModal] = useState(false)
  const queryClient = useQueryClient()

  const { data: transactions = [], isLoading } = useQuery({
    queryKey: ['transactions'],
    queryFn: () => client.get('/transactions').then(r => r.data),
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => client.delete(`/transactions/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries(['transactions'])
      queryClient.invalidateQueries(['positions'])
      queryClient.invalidateQueries(['portfolio-summary'])
    },
  })

  return (
    <Layout>
      {showAddModal && <AddTransactionModal onClose={() => setShowAddModal(false)} />}

      <div className="p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-lg font-semibold text-white">Transactions</h1>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-3 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Transaction
          </button>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          {isLoading ? (
            <div className="p-6 text-center text-slate-400 text-sm">Loading...</div>
          ) : transactions.length === 0 ? (
            <div className="p-10 text-center">
              <p className="text-slate-500 text-sm">No transactions yet</p>
              <button
                onClick={() => setShowAddModal(true)}
                className="mt-3 text-blue-400 hover:text-blue-300 text-sm"
              >
                Add your first transaction →
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-800">
                    <th className="text-left px-4 py-3 text-xs font-medium text-slate-400">Date</th>
                    <th className="text-left px-4 py-3 text-xs font-medium text-slate-400">Asset</th>
                    <th className="text-left px-4 py-3 text-xs font-medium text-slate-400">Type</th>
                    <th className="text-right px-4 py-3 text-xs font-medium text-slate-400">Qty</th>
                    <th className="text-right px-4 py-3 text-xs font-medium text-slate-400">Price</th>
                    <th className="text-right px-4 py-3 text-xs font-medium text-slate-400">Total</th>
                    <th className="text-right px-4 py-3 text-xs font-medium text-slate-400">Total USD</th>
                    <th className="text-right px-4 py-3 text-xs font-medium text-slate-400">PnL</th>
                    <th className="px-4 py-3"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {transactions.map(tx => (
                    <tr key={tx.id} className="hover:bg-slate-800/40">
                      <td className="px-4 py-3 text-slate-400 whitespace-nowrap text-xs">
                        {formatDate(tx.transaction_date)}
                      </td>
                      <td className="px-4 py-3 font-medium text-white">{tx.asset.symbol}</td>
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                          tx.transaction_type === 'buy'
                            ? 'bg-emerald-500/10 text-emerald-400'
                            : 'bg-red-500/10 text-red-400'
                        }`}>
                          {tx.transaction_type.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right text-white font-mono text-xs">{tx.quantity}</td>
                      <td className="px-4 py-3 text-right text-slate-300 text-xs whitespace-nowrap">
                        {formatCurrency(tx.price, tx.currency)} {tx.currency !== 'USD' && tx.currency}
                      </td>
                      <td className="px-4 py-3 text-right text-slate-300 text-xs whitespace-nowrap">
                        {formatCurrency(tx.total_amount, tx.currency)}
                      </td>
                      <td className="px-4 py-3 text-right text-slate-300 text-xs">
                        {tx.total_amount_usd ? formatUSD(tx.total_amount_usd) : '—'}
                      </td>
                      <td className={`px-4 py-3 text-right text-xs ${pnlColor(tx.realized_pnl)}`}>
                        {tx.transaction_type === 'sell'
                          ? `${pnlSign(tx.realized_pnl)}${formatUSD(tx.realized_pnl)}`
                          : '—'}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => deleteMutation.mutate(tx.id)}
                          disabled={deleteMutation.isPending}
                          className="text-slate-600 hover:text-red-400 transition-colors disabled:opacity-50"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}
