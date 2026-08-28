import assert from 'node:assert/strict';
import test from 'node:test';

import {
  calculateManualOpportunityScore,
  downstreamNodeIds,
  markDownstreamStale,
  orderedRunNodeIds,
  toggleDecisionSelection,
  updatePosterSection,
  type DecisionOpportunityCatalogItem,
  type DecisionScoreField,
  type PosterConfig,
  type WorkbenchEdge,
  type WorkbenchNode,
} from './workbench-model.ts';

const nodes = ['culture', 'market', 'strategy', 'brief', 'visual', 'concept-a', 'poster'].map(
  (id, index) => ({
    id,
    type:
      index === 0
        ? 'CultureGraphNode'
        : index === 1
          ? 'MarketRadarNode'
          : index === 2
            ? 'StrategyNode'
            : index === 3
              ? 'DesignBriefNode'
              : index === 4
                ? 'VisualGenerationNode'
                : index === 5
                  ? 'ConceptNode'
                  : 'PosterBoardNode',
    position: { x: index * 100, y: 0 },
    data: { label: id, eyebrow: id, title: id, summary: '', status: 'success' },
  }),
) as WorkbenchNode[];

const edges: WorkbenchEdge[] = [
  { id: 'c-s', source: 'culture', target: 'strategy' },
  { id: 'm-s', source: 'market', target: 'strategy' },
  { id: 's-b', source: 'strategy', target: 'brief' },
  { id: 'b-v', source: 'brief', target: 'visual' },
  { id: 'v-c', source: 'visual', target: 'concept-a' },
  { id: 'c-p', source: 'concept-a', target: 'poster' },
];

test('run from here uses dependency order and excludes unrelated ancestors', () => {
  assert.deepEqual(downstreamNodeIds(edges, 'brief'), ['visual', 'concept-a', 'poster']);
  assert.deepEqual(orderedRunNodeIds(nodes, edges, 'brief'), [
    'brief',
    'visual',
    'concept-a',
    'poster',
  ]);
});

test('editing an upstream node only marks descendants stale', () => {
  const updated = markDownstreamStale(nodes, edges, 'brief');
  assert.equal(updated.find((node) => node.id === 'strategy')?.data.status, 'success');
  assert.equal(updated.find((node) => node.id === 'visual')?.data.status, 'stale');
  assert.equal(updated.find((node) => node.id === 'poster')?.data.status, 'stale');
});

test('poster section visibility is reversible', () => {
  const poster: PosterConfig = {
    title: '针格模块',
    subtitle: '',
    sections: ['hero', 'culture'],
    hiddenSections: [],
    cultureElement: '',
    cultureRule: '',
    materials: [],
    process: [],
    boundary: '',
  };
  assert.deepEqual(updatePosterSection(poster, 'culture', false).hiddenSections, ['culture']);
  assert.deepEqual(
    updatePosterSection(updatePosterSection(poster, 'culture', false), 'culture', true)
      .hiddenSections,
    [],
  );
});

test('manual opportunity score normalizes weights and applies cultural risk', () => {
  const scores = {
    culture_fit: 80,
    market_pull: 80,
    novelty: 80,
    visual_potential: 80,
    social_shareability: 80,
    product_feasibility: 80,
  } satisfies Record<DecisionScoreField, number>;
  const opportunity: DecisionOpportunityCatalogItem = {
    id: 'OPP-TEST',
    cultureElement: 'test',
    trendElement: 'test',
    systemScore: 80,
    verification: 'warning',
    culturalRisk: 20,
    scores,
    evidenceRefs: [],
  };

  assert.equal(calculateManualOpportunityScore(opportunity, scores, 0.5), 65);
});

test('decision selections can be removed and respect a maximum', () => {
  assert.deepEqual(toggleDecisionSelection(['a'], 'b', 2), ['a', 'b']);
  assert.deepEqual(toggleDecisionSelection(['a', 'b'], 'c', 2), ['a', 'b']);
  assert.deepEqual(toggleDecisionSelection(['a', 'b'], 'a', 2), ['b']);
});
