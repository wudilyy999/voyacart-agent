import { useState } from 'react';
import { createRoot } from 'react-dom/client';
import ProductCards from '../src/components/ProductCards';
import ProductDetail from '../src/components/ProductDetail';
import ProductComparison from '../src/components/ProductComparison';
import ProductHistory from '../src/components/ProductHistory';
import FavoritesList from '../src/components/FavoritesList';
import MyOrders from '../src/components/MyOrders';
import { readProducts } from '../src/lib/commerceClient';
import data from './review-data.json';
import '../src/styles.css';
import '../src/components/myOrders.css';
const products = readProducts(data);
const pages = ['选购', '比较', '详情', '历史', '订单', '心选'];
const request = async () => ({total: 1, orders: [{order_id: 'DEMO-20261014-001', status: 'CONFIRMED', currency: 'CNY', total_amount_major: 210,
  created_at: '2026-10-14T08:00:00Z', shipping_address: '组件验收地址', cancel_reason: null,
  lines: [{sku_id: products[0].default_sku_id, title: products[0].title, quantity: 1, unit_price_major: 210}]}]});
function Review() {
  const [page, setPage] = useState('选购');
  const [favoriteIds, setFavorites] = useState(new Set(products.map(p => p.product_id)));
  const [comparedIds, setCompared] = useState(new Set(products.map(p => p.product_id)));
  const [selected, setSelected] = useState(products[0]);
  const detail = p => {setSelected(p); setPage('详情');};
  return <main style={{maxWidth: 1120, margin: '40px auto', padding: '0 24px', color: 'var(--ink)'}}>
    <header style={{marginBottom: 26}}><h1 style={{fontSize: 28, marginBottom: 8}}>Voyacart 商品信息</h1><p style={{fontSize: 13, color: 'var(--muted)'}}>组件验收样例：ESCI 商品原文，价格、库存与配送为演示值。</p>
      <nav style={{display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 20}}>{pages.map(item => <button key={item} onClick={() => setPage(item)} style={{padding: '8px 20px', borderRadius: 7, border: '1px solid #e0e7f2', background: page === item ? '#655dd2' : 'white', color: page === item ? 'white' : '#283650'}}>{item}</button>)}</nav>
    </header>
    {page === '选购' && <ProductCards products={products} favoriteIds={favoriteIds} comparedIds={comparedIds} onDetail={detail}
      onFavorite={p => setFavorites(ids => {const next = new Set(ids); next.has(p.product_id) ? next.delete(p.product_id) : next.add(p.product_id); return next;})}
      onCompare={p => setCompared(ids => {const next = new Set(ids); next.has(p.product_id) ? next.delete(p.product_id) : next.add(p.product_id); return next;})} />}
    {page === '详情' && <ProductDetail product={selected} busy={false} onClose={() => setPage('选购')} onCompare={() => setPage('比较')} onAsk={() => {}} onPrepare={() => {}} />}
    {page === '比较' && <ProductComparison products={products} onClose={() => setPage('选购')} />}
    {page === '历史' && <ProductHistory batches={[{runId: 'review-1', updatedAt: 1791964800000, products}]} />}
    {page === '订单' && <MyOrders request={request} confirmations={[]} busy={false} error={null} onPrepare={async () => false} onResolve={async () => false} onRefresh={async () => {}} />}
    {page === '心选' && <FavoritesList products={products.filter(p => favoriteIds.has(p.product_id))} onDetail={detail} onRemove={p => setFavorites(ids => new Set([...ids].filter(id => id !== p.product_id)))} onBrowse={() => setPage('选购')} />}
  </main>;
}
createRoot(document.getElementById('root')!).render(<Review />);
