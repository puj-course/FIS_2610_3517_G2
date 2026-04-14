import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getMatch } from '../../services/apiClient';
import useMatchStats from '../../hooks/useMatchStats';
import useMatchProbability from '../../hooks/useMatchProbability';
import Tabs from '../../components/Tabs/Tabs';
import StatsComparison from '../../components/StatsComparison/StatsComparison';
import HeadToHead from '../../components/HeadToHead/HeadToHead';
import ProbabilityBreakdown from '../../components/ProbabilityBreakdown/ProbabilityBreakdown';
import FormRecent from '../../components/FormRecent/FormRecent';
import ErrorMessage from '../../components/ErrorMessage/ErrorMessage';
import styles from './MatchDetail.module.css';

export default function MatchDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [match, setMatch] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { stats, loading: statsLoading } = useMatchStats(id);
  const { probability, loading: probLoading } = useMatchProbability(id);

  useEffect(() => {
    getMatch(id).then(setMatch).catch(e => setError(e.message)).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className={styles.loading}>Cargando partido...</div>;
  if (error) return <ErrorMessage message={error} onRetry={() => navigate('/')} />;
  if (!match) return <ErrorMessage message="Partido no encontrado" />;

  const surfaceEmoji = { clay: '🟤', grass: '🟢', hard: '🔵', carpet: '🟡' };

  const tabs = [
    { label: 'Info General', content: (
      <div className={styles.info}>
        <div className={styles.players}>
          <div className={styles.player}><h3>{match.player_home.name}</h3><span>{match.player_home.country} — Ranking #{match.player_home.ranking || 'N/A'}</span></div>
          <span className={styles.vs}>VS</span>
          <div className={styles.player}><h3>{match.player_away.name}</h3><span>{match.player_away.country} — Ranking #{match.player_away.ranking || 'N/A'}</span></div>
        </div>
        <div className={styles.details}>
          <div>{surfaceEmoji[match.tournament.surface] || '🎾'} {match.tournament.name}</div>
          <div>{match.tournament.category} — {match.tournament.location}</div>
          <div>{new Date(match.date).toLocaleString()}</div>
          <div className={styles.statusBadge} data-status={match.status}>{match.status}</div>
          {match.score && <div className={styles.score}>{match.score}</div>}
        </div>
      </div>
    )},
    { label: 'Estadísticas', content: statsLoading ? <div>Cargando estadísticas...</div> : stats ? (
      <div>
        <StatsComparison playerHomeStats={stats.player_home_stats} playerAwayStats={stats.player_away_stats} surface={stats.surface} />
        <div className={styles.formSection}>
          <h4>Forma reciente</h4>
          <div className={styles.formGrid}>
            <FormRecent form={stats.player_home_stats.recent_form} playerName={stats.player_home_stats.player_name} />
            <FormRecent form={stats.player_away_stats.recent_form} playerName={stats.player_away_stats.player_name} />
          </div>
        </div>
      </div>
    ) : <div>No hay estadísticas disponibles</div> },
    { label: 'Head-to-Head', content: statsLoading ? <div>Cargando...</div> : <HeadToHead headToHead={stats?.head_to_head} /> },
    { label: 'Probabilidad', content: probLoading ? <div>Calculando...</div> : <ProbabilityBreakdown probability={probability} /> },
  ];

  return (
    <div className={styles.page}>
      <button className={styles.back} onClick={() => navigate('/')}>← Volver a partidos</button>
      <h1 className={styles.title}>{match.player_home.name} vs {match.player_away.name}</h1>
      <Tabs tabs={tabs} />
    </div>
  );
}
