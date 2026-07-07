import React from 'react'
import {
  FiExternalLink, FiStar, FiClock, FiUsers, FiBookOpen, FiGithub
} from 'react-icons/fi'

function formatDuration(duration) {
  if (!duration) return ''
  const parts = duration.match(/(\d+)([hms])/g)
  if (!parts) return duration
  return parts.join(' ')
}

export default function LearningHub({ resources }) {
  if (!resources) return null

  const hasAny = resources.youtube?.length > 0 || resources.courses?.length > 0 ||
    resources.papers?.length > 0 || resources.github?.length > 0
  if (!hasAny) return null

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-1">
        <FiBookOpen className="text-accent-purple text-sm" />
        <h4 className="text-xs font-semibold uppercase tracking-wider text-text-muted">Learning Hub</h4>
      </div>

      {resources.youtube?.length > 0 && (
        <Section title="Videos" emoji="">
          <div className="space-y-2">
            {resources.youtube.map((video, i) => (
              <VideoCard key={i} video={video} />
            ))}
          </div>
        </Section>
      )}

      {resources.courses?.length > 0 && (
        <Section title="Courses" emoji="">
          <div className="space-y-2">
            {resources.courses.map((course, i) => (
              <CourseCard key={i} course={course} />
            ))}
          </div>
        </Section>
      )}

      {resources.papers?.length > 0 && (
        <Section title="Research Papers" emoji="">
          <div className="space-y-2">
            {resources.papers.map((paper, i) => (
              <PaperCard key={i} paper={paper} />
            ))}
          </div>
        </Section>
      )}

      {resources.github?.length > 0 && (
        <Section title="GitHub" emoji="">
          <div className="space-y-2">
            {resources.github.map((repo, i) => (
              <GitHubCard key={i} repo={repo} />
            ))}
          </div>
        </Section>
      )}
    </div>
  )
}

function Section({ title, children }) {
  return (
    <div className="animate-fadeIn">
      <h5 className="text-xs font-semibold text-text-muted mb-2 flex items-center gap-1.5">
        {title}
      </h5>
      {children}
    </div>
  )
}

function VideoCard({ video }) {
  return (
    <a
      href={video.url}
      target="_blank"
      rel="noopener noreferrer"
      className="glass rounded-xl overflow-hidden flex gap-3 p-2 hover:border-accent-cyan/40 transition-all group"
    >
      <div className="w-24 h-16 shrink-0 rounded-lg overflow-hidden bg-deep-700">
        {video.thumbnail ? (
          <img
            src={video.thumbnail}
            alt={video.title}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-text-muted text-xs">No thumbnail</div>
        )}
      </div>
      <div className="flex-1 min-w-0 flex flex-col justify-center">
        <p className="text-sm font-medium text-text-primary truncate group-hover:text-accent-cyan transition-colors">
          {video.title}
        </p>
        <p className="text-xs text-text-muted truncate mt-0.5">{video.channel}</p>
        <div className="flex items-center gap-2 mt-1">
          {video.duration && (
            <span className="text-xs text-text-muted flex items-center gap-1">
              <FiClock size={10} />
              {formatDuration(video.duration)}
            </span>
          )}
          <span className="text-xs text-accent-cyan flex items-center gap-1 ml-auto">
            Watch
            <FiExternalLink size={10} />
          </span>
        </div>
      </div>
    </a>
  )
}

function CourseCard({ course }) {
  const badgeColor = course.provider === 'Coursera'
    ? 'bg-accent-blue/10 text-accent-blue border border-accent-blue/20'
    : 'bg-accent-purple/10 text-accent-purple border border-accent-purple/20'

  return (
    <a
      href={course.url}
      target="_blank"
      rel="noopener noreferrer"
      className="glass rounded-xl p-3 hover:border-accent-green/40 transition-all group block"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${badgeColor}`}>
              {course.provider}
            </span>
          </div>
          <p className="text-sm font-medium text-text-primary truncate group-hover:text-accent-green transition-colors">
            {course.title}
          </p>
        </div>
        <span className="text-xs text-accent-green flex items-center gap-1 shrink-0">
          Open
          <FiExternalLink size={10} />
        </span>
      </div>
    </a>
  )
}

function PaperCard({ paper }) {
  const authorsDisplay = paper.authors?.slice(0, 3).join(', ')
  const hasMore = paper.authors?.length > 3

  return (
    <a
      href={paper.openalex_url || paper.pdf_url || '#'}
      target="_blank"
      rel="noopener noreferrer"
      className="glass rounded-xl p-3 hover:border-accent-yellow/40 transition-all group block"
    >
      <p className="text-sm font-medium text-text-primary leading-snug group-hover:text-accent-yellow transition-colors line-clamp-2">
        {paper.title}
      </p>
      {authorsDisplay && (
        <p className="text-xs text-text-muted mt-1 truncate">
          <FiUsers size={10} className="inline mr-1" />
          {authorsDisplay}{hasMore ? ' et al.' : ''}
        </p>
      )}
      <div className="flex items-center gap-3 mt-1.5">
        {paper.year && (
          <span className="text-xs text-text-muted">{paper.year}</span>
        )}
        {paper.citation_count !== undefined && paper.citation_count > 0 && (
          <span className="text-xs text-text-muted flex items-center gap-1">
            <FiStar size={10} className="text-accent-yellow" />
            {paper.citation_count} citations
          </span>
        )}
        <span className="text-xs text-accent-yellow flex items-center gap-1 ml-auto">
          Read
          <FiExternalLink size={10} />
        </span>
      </div>
    </a>
  )
}

function GitHubCard({ repo }) {
  return (
    <a
      href={repo.url}
      target="_blank"
      rel="noopener noreferrer"
      className="glass rounded-xl p-3 hover:border-accent-purple/40 transition-all group block"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 mb-0.5">
            <FiGithub size={12} className="text-text-muted shrink-0" />
            <p className="text-sm font-medium text-text-primary truncate group-hover:text-accent-purple transition-colors">
              {repo.repo_name}
            </p>
          </div>
          {repo.description && (
            <p className="text-xs text-text-muted line-clamp-1">{repo.description}</p>
          )}
          <div className="flex items-center gap-3 mt-1.5">
            {repo.language && (
              <span className="text-xs text-text-muted">{repo.language}</span>
            )}
            {repo.stars !== undefined && (
              <span className="text-xs text-text-muted flex items-center gap-1">
                <FiStar size={10} className="text-accent-yellow" />
                {repo.stars >= 1000 ? `${(repo.stars / 1000).toFixed(1)}k` : repo.stars}
              </span>
            )}
          </div>
        </div>
        <span className="text-xs text-accent-purple flex items-center gap-1 shrink-0">
          Open
          <FiExternalLink size={10} />
        </span>
      </div>
    </a>
  )
}
