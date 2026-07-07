"""
Graph storage routes for RabbitHole API
Save, List, Open saved graphs with notes and completion tracking
"""

import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from ..database import get_db
from ..models.user import User
from ..models.saved_graph import SavedGraph
from ..models.graph_note import GraphNote
from ..models.node_completion import NodeCompletion
from ..auth import get_current_user

router = APIRouter(prefix="/api/v1/graphs", tags=["graphs"])


class SaveGraphRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    overview: dict
    graph: dict
    node_details: dict


class SaveNotesRequest(BaseModel):
    content: str


class NodeCompletionRequest(BaseModel):
    node_id: str = Field(..., min_length=1)
    completed: bool


class GraphListItem(BaseModel):
    id: int
    topic: str
    created_at: str
    last_opened_at: str
    completed_count: int
    total_count: int
    collection_id: Optional[int] = None


class GraphDetail(BaseModel):
    id: int
    topic: str
    overview: dict
    graph: dict
    node_details: dict
    notes: str
    completions: dict
    created_at: str
    last_opened_at: str


@router.post("/save", status_code=status.HTTP_201_CREATED)
def save_graph(
    req: SaveGraphRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    graph_data = json.dumps({
        "overview": req.overview,
        "graph": req.graph,
        "node_details": req.node_details,
    })

    saved = SavedGraph(
        user_id=current_user.id,
        topic=req.topic,
        graph_data=graph_data,
    )
    db.add(saved)
    db.flush()

    note = GraphNote(saved_graph_id=saved.id, content="")
    db.add(note)
    db.commit()
    db.refresh(saved)

    return {
        "id": saved.id,
        "topic": saved.topic,
        "created_at": saved.created_at.isoformat() if saved.created_at else "",
    }


@router.put("/{graph_id}")
def update_graph(
    graph_id: int,
    req: SaveGraphRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    saved = (
        db.query(SavedGraph)
        .filter(SavedGraph.id == graph_id, SavedGraph.user_id == current_user.id)
        .first()
    )
    if not saved:
        raise HTTPException(status_code=404, detail="Graph not found")

    graph_data = json.dumps({
        "overview": req.overview,
        "graph": req.graph,
        "node_details": req.node_details,
    })

    saved.topic = req.topic
    saved.graph_data = graph_data
    saved.last_opened_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(saved)

    return {
        "id": saved.id,
        "topic": saved.topic,
        "created_at": saved.created_at.isoformat() if saved.created_at else "",
        "last_opened_at": saved.last_opened_at.isoformat() if saved.last_opened_at else "",
    }


@router.get("/list", response_model=list[GraphListItem])
def list_graphs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    saved_graphs = (
        db.query(SavedGraph)
        .filter(SavedGraph.user_id == current_user.id)
        .order_by(SavedGraph.last_opened_at.desc())
        .all()
    )

    result = []
    for g in saved_graphs:
        total_count = 0
        completed_count = 0
        try:
            data = json.loads(g.graph_data)
            total_count = len(data.get("graph", {}).get("nodes", []))
            completed_count = (
                db.query(func.count(NodeCompletion.id))
                .filter(
                    NodeCompletion.saved_graph_id == g.id,
                    NodeCompletion.completed == True,
                )
                .scalar()
                or 0
            )
        except (json.JSONDecodeError, KeyError):
            pass

        result.append(GraphListItem(
            id=g.id,
            topic=g.topic,
            created_at=g.created_at.isoformat() if g.created_at else "",
            last_opened_at=g.last_opened_at.isoformat() if g.last_opened_at else "",
            completed_count=completed_count,
            total_count=total_count,
            collection_id=g.collection_id,
        ))

    return result


@router.get("/open/{graph_id}", response_model=GraphDetail)
def open_graph(
    graph_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    saved = (
        db.query(SavedGraph)
        .filter(SavedGraph.id == graph_id, SavedGraph.user_id == current_user.id)
        .first()
    )
    if not saved:
        raise HTTPException(status_code=404, detail="Graph not found")

    saved.last_opened_at = datetime.now(timezone.utc)
    db.commit()

    try:
        data = json.loads(saved.graph_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Corrupted graph data")

    note = db.query(GraphNote).filter(GraphNote.saved_graph_id == graph_id).first()
    notes_content = note.content if note else ""

    completions = db.query(NodeCompletion).filter(
        NodeCompletion.saved_graph_id == graph_id
    ).all()
    completions_dict = {c.node_id: c.completed for c in completions}

    return GraphDetail(
        id=saved.id,
        topic=saved.topic,
        overview=data.get("overview", {}),
        graph=data.get("graph", {"nodes": [], "edges": []}),
        node_details=data.get("node_details", {}),
        notes=notes_content,
        completions=completions_dict,
        created_at=saved.created_at.isoformat() if saved.created_at else "",
        last_opened_at=saved.last_opened_at.isoformat() if saved.last_opened_at else "",
    )


@router.put("/{graph_id}/notes")
def save_notes(
    graph_id: int,
    req: SaveNotesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    saved = (
        db.query(SavedGraph)
        .filter(SavedGraph.id == graph_id, SavedGraph.user_id == current_user.id)
        .first()
    )
    if not saved:
        raise HTTPException(status_code=404, detail="Graph not found")

    note = db.query(GraphNote).filter(GraphNote.saved_graph_id == graph_id).first()
    if not note:
        note = GraphNote(saved_graph_id=graph_id, content=req.content)
        db.add(note)
    else:
        note.content = req.content
    db.commit()

    return {"content": req.content}


@router.get("/{graph_id}/notes")
def load_notes(
    graph_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    saved = (
        db.query(SavedGraph)
        .filter(SavedGraph.id == graph_id, SavedGraph.user_id == current_user.id)
        .first()
    )
    if not saved:
        raise HTTPException(status_code=404, detail="Graph not found")

    note = db.query(GraphNote).filter(GraphNote.saved_graph_id == graph_id).first()
    return {"content": note.content if note else ""}


@router.put("/{graph_id}/completion")
def update_completion(
    graph_id: int,
    req: NodeCompletionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    saved = (
        db.query(SavedGraph)
        .filter(SavedGraph.id == graph_id, SavedGraph.user_id == current_user.id)
        .first()
    )
    if not saved:
        raise HTTPException(status_code=404, detail="Graph not found")

    completion = (
        db.query(NodeCompletion)
        .filter(
            NodeCompletion.saved_graph_id == graph_id,
            NodeCompletion.node_id == req.node_id,
        )
        .first()
    )

    if completion:
        completion.completed = req.completed
    else:
        completion = NodeCompletion(
            saved_graph_id=graph_id,
            node_id=req.node_id,
            completed=req.completed,
        )
        db.add(completion)
    db.commit()

    total_count = 0
    try:
        data = json.loads(saved.graph_data)
        total_count = len(data.get("graph", {}).get("nodes", []))
    except (json.JSONDecodeError, KeyError):
        pass

    completed_count = (
        db.query(func.count(NodeCompletion.id))
        .filter(
            NodeCompletion.saved_graph_id == graph_id,
            NodeCompletion.completed == True,
        )
        .scalar()
        or 0
    )

    return {
        "completed": req.completed,
        "completed_count": completed_count,
        "total_count": total_count,
    }


@router.delete("/{graph_id}")
def delete_graph(
    graph_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    saved = (
        db.query(SavedGraph)
        .filter(SavedGraph.id == graph_id, SavedGraph.user_id == current_user.id)
        .first()
    )
    if not saved:
        raise HTTPException(status_code=404, detail="Graph not found")

    db.query(NodeCompletion).filter(NodeCompletion.saved_graph_id == graph_id).delete()
    db.query(GraphNote).filter(GraphNote.saved_graph_id == graph_id).delete()
    db.delete(saved)
    db.commit()

    return {"deleted": True}


@router.get("/{graph_id}/progress")
def get_progress(
    graph_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    saved = (
        db.query(SavedGraph)
        .filter(SavedGraph.id == graph_id, SavedGraph.user_id == current_user.id)
        .first()
    )
    if not saved:
        raise HTTPException(status_code=404, detail="Graph not found")

    total_count = 0
    try:
        data = json.loads(saved.graph_data)
        total_count = len(data.get("graph", {}).get("nodes", []))
    except (json.JSONDecodeError, KeyError):
        pass

    completed_count = (
        db.query(func.count(NodeCompletion.id))
        .filter(
            NodeCompletion.saved_graph_id == graph_id,
            NodeCompletion.completed == True,
        )
        .scalar()
        or 0
    )

    return {
        "completed_count": completed_count,
        "total_count": total_count,
    }
