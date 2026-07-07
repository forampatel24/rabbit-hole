import json
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models.user import User
from ..models.collection import Collection
from ..models.saved_graph import SavedGraph
from ..models.node_completion import NodeCompletion
from ..models.graph_note import GraphNote
from ..auth import get_current_user
from ..models.schemas import (
    CollectionCreate,
    CollectionRename,
    CollectionResponse,
    CollectionDetail,
    GraphMoveRequest,
    GraphCopyRequest,
    SearchResult,
    SearchResults,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/collections", tags=["collections"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_collection(
    req: CollectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    collection = Collection(user_id=current_user.id, name=req.name.strip())
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return {
        "id": collection.id,
        "name": collection.name,
        "created_at": collection.created_at.isoformat() if collection.created_at else "",
    }


@router.get("", response_model=List[CollectionResponse])
def list_collections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    collections = (
        db.query(Collection)
        .filter(Collection.user_id == current_user.id)
        .order_by(Collection.created_at.desc())
        .all()
    )

    result = []
    for c in collections:
        count = db.query(func.count(SavedGraph.id)).filter(
            SavedGraph.collection_id == c.id,
            SavedGraph.user_id == current_user.id,
        ).scalar() or 0
        result.append(CollectionResponse(
            id=c.id,
            name=c.name,
            created_at=c.created_at.isoformat() if c.created_at else "",
            graph_count=count,
        ))
    return result


@router.get("/{collection_id}", response_model=CollectionDetail)
def get_collection(
    collection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.user_id == current_user.id,
    ).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    graphs = (
        db.query(SavedGraph)
        .filter(
            SavedGraph.collection_id == collection_id,
            SavedGraph.user_id == current_user.id,
        )
        .order_by(SavedGraph.last_opened_at.desc())
        .all()
    )

    graph_list = []
    for g in graphs:
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
                .scalar() or 0
            )
        except (json.JSONDecodeError, KeyError):
            pass
        graph_list.append({
            "id": g.id,
            "topic": g.topic,
            "created_at": g.created_at.isoformat() if g.created_at else "",
            "last_opened_at": g.last_opened_at.isoformat() if g.last_opened_at else "",
            "completed_count": completed_count,
            "total_count": total_count,
        })

    return CollectionDetail(
        id=collection.id,
        name=collection.name,
        created_at=collection.created_at.isoformat() if collection.created_at else "",
        graphs=graph_list,
    )


@router.put("/{collection_id}")
def rename_collection(
    collection_id: int,
    req: CollectionRename,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.user_id == current_user.id,
    ).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    collection.name = req.name.strip()
    db.commit()
    return {"id": collection.id, "name": collection.name}


@router.delete("/{collection_id}")
def delete_collection(
    collection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.user_id == current_user.id,
    ).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    db.query(SavedGraph).filter(SavedGraph.collection_id == collection_id).update(
        {"collection_id": None}
    )
    db.delete(collection)
    db.commit()
    return {"deleted": True}


@router.put("/{collection_id}/graphs/{graph_id}/move")
def move_graph(
    collection_id: int,
    graph_id: int,
    req: GraphMoveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    graph = db.query(SavedGraph).filter(
        SavedGraph.id == graph_id,
        SavedGraph.user_id == current_user.id,
    ).first()
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")

    if req.target_collection_id is not None:
        target = db.query(Collection).filter(
            Collection.id == req.target_collection_id,
            Collection.user_id == current_user.id,
        ).first()
        if not target:
            raise HTTPException(status_code=404, detail="Target collection not found")

    graph.collection_id = req.target_collection_id
    db.commit()
    return {"id": graph.id, "collection_id": graph.collection_id}


@router.put("/{collection_id}/graphs/{graph_id}/copy")
def copy_graph(
    collection_id: int,
    graph_id: int,
    req: GraphCopyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    original = db.query(SavedGraph).filter(
        SavedGraph.id == graph_id,
        SavedGraph.user_id == current_user.id,
    ).first()
    if not original:
        raise HTTPException(status_code=404, detail="Graph not found")

    target = db.query(Collection).filter(
        Collection.id == req.target_collection_id,
        Collection.user_id == current_user.id,
    ).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target collection not found")

    copied = SavedGraph(
        user_id=current_user.id,
        collection_id=req.target_collection_id,
        topic=original.topic,
        graph_data=original.graph_data,
    )
    db.add(copied)
    db.flush()

    note = db.query(GraphNote).filter(GraphNote.saved_graph_id == graph_id).first()
    new_note = GraphNote(saved_graph_id=copied.id, content=note.content if note else "")
    db.add(new_note)
    db.commit()
    db.refresh(copied)

    return {
        "id": copied.id,
        "topic": copied.topic,
        "collection_id": copied.collection_id,
    }


@router.put("/{collection_id}/graphs/{graph_id}/remove")
def remove_from_collection(
    collection_id: int,
    graph_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    graph = db.query(SavedGraph).filter(
        SavedGraph.id == graph_id,
        SavedGraph.collection_id == collection_id,
        SavedGraph.user_id == current_user.id,
    ).first()
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found in this collection")
    graph.collection_id = None
    db.commit()
    return {"id": graph.id, "collection_id": None}


@router.get("/search/query", response_model=SearchResults)
def search_graphs(
    q: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = q.strip()
    if not query:
        return SearchResults(results=[])

    search_term = f"%{query}%"
    graphs = (
        db.query(SavedGraph)
        .filter(
            SavedGraph.user_id == current_user.id,
            SavedGraph.topic.ilike(search_term),
        )
        .order_by(SavedGraph.last_opened_at.desc())
        .limit(20)
        .all()
    )

    results = []
    for g in graphs:
        collection_name = None
        if g.collection_id:
            coll = db.query(Collection).filter(Collection.id == g.collection_id).first()
            collection_name = coll.name if coll else None

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
                .scalar() or 0
            )
        except (json.JSONDecodeError, KeyError):
            pass

        results.append(SearchResult(
            id=g.id,
            topic=g.topic,
            collection_name=collection_name,
            collection_id=g.collection_id,
            created_at=g.created_at.isoformat() if g.created_at else "",
            completed_count=completed_count,
            total_count=total_count,
        ))

    return SearchResults(results=results)
