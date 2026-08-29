'use client';

import { Maximize2, Move, Search, ZoomIn, ZoomOut } from 'lucide-react';
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent,
  type PointerEvent,
} from 'react';

import type { CultureRecordSummary, EvidenceCitation } from './workbench-model';

type RawRecord = CultureRecordSummary | Record<string, unknown>;

interface ConstellationRecord {
  id: string;
  name: string;
  category: string;
  region: string[];
  crafts: string[];
  patterns: string[];
  boundaries: string[];
  modernizable: string[];
  history: string[];
  sourceRefs: string[];
}

interface PositionedNode {
  id: string;
  x: number;
  y: number;
}

interface PositionedRecord extends PositionedNode {
  record: ConstellationRecord;
  categoryId: string;
}

interface PositionedSource extends PositionedNode {
  ref: string;
}

interface PinchGesture {
  distance: number;
  centerX: number;
  centerY: number;
  zoom: number;
  pan: { x: number; y: number };
}

function strings(value: unknown): string[] {
  return Array.isArray(value) ? value.map(String).filter(Boolean) : [];
}

function field(record: RawRecord, snake: string, camel: string): unknown {
  const payload = record as Record<string, unknown>;
  return payload[snake] ?? payload[camel];
}

function normalizeRecord(record: RawRecord): ConstellationRecord {
  return {
    id: String(field(record, 'culture_id', 'id') ?? ''),
    name: String(field(record, 'culture_name', 'name') ?? '未命名文化记录'),
    category: String(field(record, 'category', 'category') ?? '在地文化'),
    region: strings(field(record, 'region', 'region')),
    crafts: strings(field(record, 'crafts', 'crafts')),
    patterns: strings(field(record, 'patterns', 'patterns')),
    boundaries: strings(
      field(record, 'cultural_taboos', 'boundaries')
      ?? field(record, 'non_transferable_elements', 'boundaries'),
    ),
    modernizable: strings(field(record, 'modernizable_elements', 'modernizable')),
    history: strings(field(record, 'history', 'history')),
    sourceRefs: strings(field(record, 'source_refs', 'sourceRefs')),
  };
}

function stableHash(value: string): number {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

function clamp(value: number, minimum: number, maximum: number): number {
  return Math.max(minimum, Math.min(maximum, value));
}

function buildLayout(records: ConstellationRecord[]) {
  const categories = Array.from(new Set(records.map((record) => record.category))).sort();
  const categoryNodes = categories.map((category, index) => {
    const angle = -Math.PI / 2 + (index / Math.max(categories.length, 1)) * Math.PI * 2;
    return {
      id: `category:${category}`,
      label: category,
      x: Math.cos(angle) * 220,
      y: Math.sin(angle) * 220,
      angle,
    };
  });
  const positionedRecords: PositionedRecord[] = [];
  categoryNodes.forEach((category) => {
    const group = records.filter((record) => record.category === category.label);
    group.forEach((record, index) => {
      const centeredIndex = index - (group.length - 1) / 2;
      const angle = category.angle + centeredIndex * 0.19;
      const jitter = (stableHash(record.id) % 46) - 23;
      const radius = 355 + (index % 2) * 62 + jitter;
      positionedRecords.push({
        id: record.id,
        x: Math.cos(angle) * radius,
        y: Math.sin(angle) * radius,
        record,
        categoryId: category.id,
      });
    });
  });
  const sourceRefs = Array.from(new Set(records.flatMap((record) => record.sourceRefs))).sort();
  const sourceNodes: PositionedSource[] = sourceRefs.map((ref, index) => {
    const hash = stableHash(ref);
    const angle = (index / Math.max(sourceRefs.length, 1)) * Math.PI * 2 + (hash % 17) / 100;
    const radius = 535 + (hash % 54);
    return { id: `source:${ref}`, ref, x: Math.cos(angle) * radius, y: Math.sin(angle) * radius };
  });
  const recordById = new Map(positionedRecords.map((item) => [item.id, item]));
  const categoryById = new Map(categoryNodes.map((item) => [item.id, item]));
  const sourceByRef = new Map(sourceNodes.map((item) => [item.ref, item]));
  return {
    categoryNodes,
    positionedRecords,
    sourceNodes,
    recordById,
    categoryById,
    sourceByRef,
  };
}

function StarField() {
  const points = useMemo(() => Array.from({ length: 92 }, (_, index) => {
    const hash = stableHash(`star-${index}`);
    return {
      x: (hash % 1160) - 580,
      y: ((Math.floor(hash / 1160) % 720) - 360),
      radius: index % 9 === 0 ? 1.6 : index % 3 === 0 ? 1.1 : 0.7,
      opacity: 0.12 + (hash % 34) / 100,
    };
  }), []);
  return (
    <g className="constellation-star-field" aria-hidden="true">
      {points.map((point, index) => (
        <circle key={index} cx={point.x} cy={point.y} opacity={point.opacity} r={point.radius} />
      ))}
    </g>
  );
}

function RecordInspector({
  record,
  sourceMap,
}: {
  record: ConstellationRecord;
  sourceMap: Map<string, EvidenceCitation>;
}) {
  return (
    <aside className="constellation-inspector">
      <header>
        <span>{record.category}</span>
        <code>{record.id}</code>
      </header>
      <h3>{record.name}</h3>
      <p className="constellation-record-lead">{record.history[0] ?? '已进入结构化文化知识图谱。'}</p>
      <dl>
        <div><dt>地域</dt><dd>{record.region.slice(0, 5).join(' · ') || '待补充'}</dd></div>
        <div><dt>工艺</dt><dd>{record.crafts.slice(0, 6).join(' · ') || '待补充'}</dd></div>
        <div><dt>纹样 / 结构</dt><dd>{record.patterns.slice(0, 6).join(' · ') || '待补充'}</dd></div>
      </dl>
      {record.modernizable.length ? (
        <section><h4>可转译方向</h4><ul>{record.modernizable.slice(0, 4).map((item) => <li key={item}>{item}</li>)}</ul></section>
      ) : null}
      {record.boundaries.length ? (
        <section className="constellation-boundary"><h4>文化边界</h4><p>{record.boundaries[0]}</p></section>
      ) : null}
      <div className="constellation-source-links">
        {record.sourceRefs.slice(0, 12).map((ref) => (
          <a href={`#citation-${ref}`} key={ref} title={sourceMap.get(ref)?.title ?? ref}>{ref}</a>
        ))}
      </div>
    </aside>
  );
}

export function CultureConstellation({
  records,
  citations = [],
  selectedId,
  onSelectionChange,
  compact = false,
}: {
  records: RawRecord[];
  citations?: EvidenceCitation[];
  selectedId?: string;
  onSelectionChange?: (id: string) => void;
  compact?: boolean;
}) {
  const normalized = useMemo(() => records.map(normalizeRecord).filter((record) => record.id), [records]);
  const [internalSelectedId, setInternalSelectedId] = useState(normalized[0]?.id ?? '');
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('all');
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [drag, setDrag] = useState<{ pointerId: number; x: number; y: number } | null>(null);
  const [touchMode, setTouchMode] = useState(false);
  const svgRef = useRef<SVGSVGElement>(null);
  const pointersRef = useRef(new Map<number, { x: number; y: number }>());
  const pinchRef = useRef<PinchGesture | null>(null);
  const activeId = (selectedId ?? internalSelectedId) || normalized[0]?.id || '';
  const layout = useMemo(() => buildLayout(normalized), [normalized]);
  const sourceMap = useMemo(() => new Map(citations.map((item) => [item.id, item])), [citations]);
  const categories = useMemo(() => Array.from(new Set(normalized.map((record) => record.category))).sort(), [normalized]);
  const selected = normalized.find((record) => record.id === activeId) ?? normalized[0];
  const visibleIds = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return new Set(normalized.filter((record) => {
      if (category !== 'all' && record.category !== category) return false;
      if (!needle) return true;
      return [record.name, record.category, ...record.region, ...record.crafts, ...record.patterns]
        .join(' ')
        .toLowerCase()
        .includes(needle);
    }).map((record) => record.id));
  }, [category, normalized, query]);
  const selectedSources = new Set(selected?.sourceRefs ?? []);

  const selectRecord = useCallback((id: string) => {
    if (selectedId === undefined) setInternalSelectedId(id);
    onSelectionChange?.(id);
  }, [onSelectionChange, selectedId]);

  const focusSingleMatch = useCallback((nextQuery: string, nextCategory: string) => {
    if (!nextQuery.trim() && nextCategory === 'all') return;
    const needle = nextQuery.trim().toLowerCase();
    const matches = normalized.filter((record) => {
      if (nextCategory !== 'all' && record.category !== nextCategory) return false;
      if (!needle) return true;
      return [record.name, record.category, ...record.region, ...record.crafts, ...record.patterns]
        .join(' ')
        .toLowerCase()
        .includes(needle);
    });
    if (matches.length !== 1) return;
    const node = layout.recordById.get(matches[0].id);
    if (!node) return;
    const focusZoom = 1.35;
    selectRecord(matches[0].id);
    setZoom(focusZoom);
    setPan({ x: -node.x * focusZoom, y: -node.y * focusZoom });
  }, [layout.recordById, normalized, selectRecord]);

  const resetView = useCallback(() => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  }, []);

  const clearGesture = useCallback(() => {
    pointersRef.current.clear();
    pinchRef.current = null;
    setDrag(null);
  }, []);

  const toggleTouchMode = useCallback(() => {
    clearGesture();
    setTouchMode((current) => !current);
  }, [clearGesture]);

  const onPointerDown = useCallback((event: PointerEvent<SVGSVGElement>) => {
    if (event.pointerType === 'touch' && !touchMode) return;
    const target = event.target as Element;
    if (event.pointerType !== 'touch' && target.closest('[data-constellation-node]')) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    pointersRef.current.set(event.pointerId, { x: event.clientX, y: event.clientY });
    const pointers = [...pointersRef.current.entries()];
    if (pointers.length >= 2) {
      const [, first] = pointers[0];
      const [, second] = pointers[1];
      pinchRef.current = {
        distance: Math.hypot(second.x - first.x, second.y - first.y),
        centerX: (first.x + second.x) / 2,
        centerY: (first.y + second.y) / 2,
        zoom,
        pan,
      };
      setDrag(null);
      return;
    }
    setDrag({ pointerId: event.pointerId, x: event.clientX, y: event.clientY });
  }, [pan, touchMode, zoom]);

  const onPointerMove = useCallback((event: PointerEvent<SVGSVGElement>) => {
    if (pointersRef.current.has(event.pointerId)) {
      pointersRef.current.set(event.pointerId, { x: event.clientX, y: event.clientY });
    }
    const pointers = [...pointersRef.current.values()];
    if (pointers.length >= 2) {
      event.preventDefault();
      const first = pointers[0];
      const second = pointers[1];
      const gesture = pinchRef.current;
      if (!gesture) return;
      const distance = Math.max(1, Math.hypot(second.x - first.x, second.y - first.y));
      const centerX = (first.x + second.x) / 2;
      const centerY = (first.y + second.y) / 2;
      const width = svgRef.current?.getBoundingClientRect().width || 1200;
      const worldPerPixel = 1200 / width;
      setZoom(clamp(gesture.zoom * (distance / Math.max(1, gesture.distance)), 0.65, 2.2));
      setPan({
        x: gesture.pan.x + (centerX - gesture.centerX) * worldPerPixel,
        y: gesture.pan.y + (centerY - gesture.centerY) * worldPerPixel,
      });
      return;
    }
    if (!drag || drag.pointerId !== event.pointerId) return;
    const width = svgRef.current?.getBoundingClientRect().width || 1200;
    const worldPerPixel = 1200 / width / zoom;
    setPan((current) => ({
      x: current.x + (event.clientX - drag.x) * worldPerPixel,
      y: current.y + (event.clientY - drag.y) * worldPerPixel,
    }));
    setDrag({ pointerId: drag.pointerId, x: event.clientX, y: event.clientY });
  }, [drag, zoom]);

  const endDrag = useCallback((event: PointerEvent<SVGSVGElement>) => {
    pointersRef.current.delete(event.pointerId);
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
    const remaining = [...pointersRef.current.entries()];
    pinchRef.current = null;
    if (remaining.length === 1) {
      const [pointerId, point] = remaining[0];
      setDrag({ pointerId, x: point.x, y: point.y });
    } else {
      setDrag(null);
    }
  }, []);

  useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return undefined;
    const onWheel = (event: WheelEvent) => {
      event.preventDefault();
      setZoom((current) => clamp(current * (event.deltaY > 0 ? 0.9 : 1.1), 0.65, 2.2));
    };
    svg.addEventListener('wheel', onWheel, { passive: false });
    return () => svg.removeEventListener('wheel', onWheel);
  }, []);

  const onKeyDown = useCallback((event: KeyboardEvent<SVGSVGElement>) => {
    const step = event.shiftKey ? 80 : 34;
    if (event.key === 'ArrowLeft') setPan((current) => ({ ...current, x: current.x + step }));
    else if (event.key === 'ArrowRight') setPan((current) => ({ ...current, x: current.x - step }));
    else if (event.key === 'ArrowUp') setPan((current) => ({ ...current, y: current.y + step }));
    else if (event.key === 'ArrowDown') setPan((current) => ({ ...current, y: current.y - step }));
    else if (event.key === '+' || event.key === '=') setZoom((current) => clamp(current * 1.12, 0.65, 2.2));
    else if (event.key === '-') setZoom((current) => clamp(current * 0.88, 0.65, 2.2));
    else if (event.key === '0') resetView();
    else return;
    event.preventDefault();
  }, [resetView]);

  if (!selected) return <p className="detail-empty">文化图谱暂无记录。</p>;
  return (
    <section className={`culture-constellation ${compact ? 'is-compact' : ''}`}>
      <div className={`constellation-stage ${drag ? 'is-dragging' : ''} ${touchMode ? 'is-touch-active' : ''}`}>
        <header className="constellation-toolbar">
          <label className="constellation-search">
            <Search aria-hidden="true" size={15} />
            <span className="sr-only">搜索文化记录</span>
            <input placeholder="搜索地域、工艺、纹样" value={query} onChange={(event) => { const value = event.target.value; setQuery(value); focusSingleMatch(value, category); }} />
          </label>
          <select aria-label="按文化分类筛选" value={category} onChange={(event) => { const value = event.target.value; setCategory(value); focusSingleMatch(query, value); }}>
            <option value="all">全部分类</option>
            {categories.map((item) => <option key={item} value={item}>{item}</option>)}
          </select>
          <span className="constellation-result-count">{visibleIds.size} / {normalized.length}</span>
        </header>
        <div className="constellation-controls" aria-label="星图视图控制">
          <button aria-label="放大星图" type="button" onClick={() => setZoom((current) => clamp(current * 1.15, 0.65, 2.2))}><ZoomIn aria-hidden="true" size={16} /></button>
          <button aria-label="缩小星图" type="button" onClick={() => setZoom((current) => clamp(current * 0.85, 0.65, 2.2))}><ZoomOut aria-hidden="true" size={16} /></button>
          <button aria-label="重置星图视图" type="button" onClick={resetView}><Maximize2 aria-hidden="true" size={16} /></button>
        </div>
        <div className="constellation-instruction">
          <Move aria-hidden="true" size={14} />
          <span className="is-desktop-instruction">拖动画布 · 滚轮缩放 · 点击星点查看</span>
          <span className="is-touch-instruction">{touchMode ? '单指平移 · 双指缩放' : '页面可上下滚动'}</span>
          <button aria-pressed={touchMode} type="button" onClick={toggleTouchMode}>{touchMode ? '完成' : '操作星图'}</button>
        </div>
        <svg
          aria-label="贵州在地文化关系星图。桌面可拖动和滚轮缩放；触屏先开启操作星图，再用单指平移、双指缩放。"
          onKeyDown={onKeyDown}
          onPointerCancel={endDrag}
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={endDrag}
          ref={svgRef}
          role="application"
          tabIndex={0}
          viewBox="-600 -380 1200 760"
        >
          <rect className="constellation-hit-area" height="760" width="1200" x="-600" y="-380" />
          <g transform={`translate(${pan.x} ${pan.y}) scale(${zoom})`}>
            <StarField />
            <g className="constellation-edges" aria-hidden="true">
              {layout.categoryNodes.map((node) => (
                <line key={`root-${node.id}`} x1="0" y1="0" x2={node.x} y2={node.y} />
              ))}
              {layout.positionedRecords.map((node) => {
                const categoryNode = layout.categoryById.get(node.categoryId);
                if (!categoryNode) return null;
                return (
                  <line
                    className={node.id === activeId ? 'is-active' : visibleIds.has(node.id) ? '' : 'is-dimmed'}
                    key={`category-${node.id}`}
                    x1={categoryNode.x}
                    y1={categoryNode.y}
                    x2={node.x}
                    y2={node.y}
                  />
                );
              })}
              {layout.positionedRecords.flatMap((node) => node.record.sourceRefs.map((ref) => {
                const source = layout.sourceByRef.get(ref);
                if (!source) return null;
                return (
                  <line
                    className={node.id === activeId && selectedSources.has(ref) ? 'is-source-active' : 'is-source'}
                    key={`${node.id}-${ref}`}
                    x1={node.x}
                    y1={node.y}
                    x2={source.x}
                    y2={source.y}
                  />
                );
              }))}
            </g>
            <g className="constellation-source-nodes" aria-hidden="true">
              {layout.sourceNodes.map((source) => (
                <circle className={selectedSources.has(source.ref) ? 'is-active' : ''} cx={source.x} cy={source.y} key={source.id} r={selectedSources.has(source.ref) ? 3.5 : 2} />
              ))}
            </g>
            <g className="constellation-category-nodes" aria-hidden="true">
              {layout.categoryNodes.map((node) => (
                <g key={node.id} transform={`translate(${node.x} ${node.y})`}>
                  <circle r="16" />
                  <text y="31">{node.label}</text>
                </g>
              ))}
            </g>
            <g
              aria-label="贵州在地文化"
              className="constellation-core"
              data-constellation-node
              onClick={resetView}
              role="button"
              tabIndex={-1}
            >
              <circle r="44" />
              <circle className="is-orbit" r="62" />
              <circle className="is-hit" r="44" />
              <text y="-3">贵州</text>
              <text className="is-small" y="17">在地文化</text>
            </g>
            <g className="constellation-record-nodes">
              {layout.positionedRecords.map((node) => {
                const active = node.id === activeId;
                const visible = visibleIds.has(node.id);
                return (
                  <g
                    aria-label={`${node.record.name}，${node.record.category}，${node.record.sourceRefs.length} 条来源`}
                    className={`${active ? 'is-active' : ''} ${visible ? '' : 'is-dimmed'}`}
                    data-constellation-node
                    key={node.id}
                    onClick={() => selectRecord(node.id)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault();
                        selectRecord(node.id);
                      }
                    }}
                    role="button"
                    tabIndex={visible ? 0 : -1}
                    transform={`translate(${node.x} ${node.y})`}
                  >
                    <circle className="is-hit" r="20" />
                    <circle className="is-node" r="6.5" />
                    <circle className="is-ring" r="13" />
                    <text className="is-name" textAnchor={node.x < 0 ? 'start' : 'end'} x={node.x < 0 ? 25 : -25} y="4">{node.record.name}</text>
                  </g>
                );
              })}
            </g>
          </g>
        </svg>
        <div className="constellation-legend" aria-hidden="true"><span><i className="is-record" />文化记录</span><span><i className="is-source" />公开来源</span><span><i className="is-category" />分类引力点</span></div>
      </div>
      <RecordInspector record={selected} sourceMap={sourceMap} />
    </section>
  );
}
