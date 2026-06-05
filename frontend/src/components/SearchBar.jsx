import React, {useState, useContext} from 'react'
import { GraphContext } from '../context/GraphContext'

export default function SearchBar(){
  const [value,setValue] = useState('')
  const { generateGraph } = useContext(GraphContext)
  return (
    <div className="p-4 flex gap-2">
      <input className="flex-1 p-2 rounded bg-[#0B1220] text-[#F8FAFC] border border-[#23303F]" placeholder="Enter topic e.g. Transformers" value={value} onChange={e=>setValue(e.target.value)} />
      <button className="px-4 py-2 rounded bg-[#3B82F6] text-black" onClick={()=>generateGraph(value)}>Generate Map</button>
    </div>
  )
}
