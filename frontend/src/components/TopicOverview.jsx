import React, {useContext} from 'react'
import { GraphContext } from '../context/GraphContext'

export default function TopicOverview(){
  const { overview } = useContext(GraphContext)
  if(!overview) return null
  return (
    <div className="p-4 bg-[#071027] text-[#F8FAFC] rounded">
      <h2 className="text-xl font-semibold">{overview.topic}</h2>
      <p className="text-sm text-[#94A3B8]">{overview.domain} • {overview.difficulty} • {overview.popularity}</p>
      <p className="mt-2 text-sm">{overview.summary}</p>
    </div>
  )
}
