import React, {useContext, useRef, useEffect} from 'react'
import ReactFlow, {Background, Controls} from 'reactflow'
import 'reactflow/dist/style.css'
import { GraphContext } from '../context/GraphContext'

export default function GraphView(){
  const { graph, openNodePanel, setGraph } = useContext(GraphContext)
  const nodes = (graph?.nodes || []).map(n=>({id:n.id, data:{label:n.name}, position: n.position || {x: Math.random()*400, y: Math.random()*400}}))
  const edges = (graph?.edges || []).map(e=>({id:e.id || `${e.source}-${e.target}`, source:e.source, target:e.target, label: e.relationship}))

  return (
    <div className="flex-1 bg-[#071127]">
      <ReactFlow nodes={nodes} edges={edges} onNodeClick={(e, node)=>openNodePanel(node.id)} style={{width:'100%', height:'600px'}}>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  )
}
