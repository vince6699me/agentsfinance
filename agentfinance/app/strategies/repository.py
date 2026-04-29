"""
AgentFinance v5 - Strategy Repository

Database repository for managing strategies in SQLite.
Provides CRUD operations and seed data loading for all 46 strategies and 7 tactics.
"""

import logging
from typing import List, Optional, Dict
from datetime import datetime

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strategies import Strategy
from app.strategies.registry import StrategyRegistry, StrategyDefinition, strategy_registry

logger = logging.getLogger(__name__)


class StrategyRepository:
    """
    Repository for managing trading strategies in the database.
    
    Provides methods for:
    - CRUD operations on strategies
    - Bulk loading seed data
    - Querying by category, tier, sector, department
    - Strategy lookup by ID
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.registry = strategy_registry
    
    async def get_by_id(self, strategy_id: int) -> Optional[Strategy]:
        """Get a strategy by database ID."""
        result = await self.session.execute(
            select(Strategy).where(Strategy.id == strategy_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_strategy_id(self, strategy_id: str) -> Optional[Strategy]:
        """Get a strategy by its strategy ID (e.g., 'ICT-01')."""
        result = await self.session.execute(
            select(Strategy).where(Strategy.strategy_id == strategy_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Strategy]:
        """Get all strategies with optional pagination."""
        query = select(Strategy).offset(offset)
        if limit:
            query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_by_category(self, category: str) -> List[Strategy]:
        """Get all strategies in a category."""
        result = await self.session.execute(
            select(Strategy).where(Strategy.category == category)
        )
        return list(result.scalars().all())
    
    async def get_by_tier(self, tier: str) -> List[Strategy]:
        """Get all strategies of a specific tier."""
        result = await self.session.execute(
            select(Strategy).where(Strategy.tier == tier)
        )
        return list(result.scalars().all())
    
    async def get_by_sector(self, sector: str) -> List[Strategy]:
        """Get all strategies applicable to a sector."""
        # Use LIKE for partial match (e.g., 'forex' matches 'forex,commodities')
        result = await self.session.execute(
            select(Strategy).where(Strategy.sector.like(f"%{sector}%"))
        )
        return list(result.scalars().all())
    
    async def get_by_department(self, department: str) -> List[Strategy]:
        """Get all strategies owned by a department."""
        result = await self.session.execute(
            select(Strategy).where(Strategy.department == department)
        )
        return list(result.scalars().all())
    
    async def get_tactics(self) -> List[Strategy]:
        """Get all execution tactics."""
        result = await self.session.execute(
            select(Strategy).where(Strategy.is_tactic == True)
        )
        return list(result.scalars().all())
    
    async def get_active(self) -> List[Strategy]:
        """Get all active strategies."""
        result = await self.session.execute(
            select(Strategy).where(Strategy.status == "active")
        )
        return list(result.scalars().all())
    
    async def get_v2_enabled(self) -> List[Strategy]:
        """Get all strategies with v2 enhancements enabled."""
        result = await self.session.execute(
            select(Strategy).where(Strategy.v2_enabled == True)
        )
        return list(result.scalars().all())
    
    async def search(self, keyword: str) -> List[Strategy]:
        """Search strategies by keyword in name or description."""
        keyword_pattern = f"%{keyword}%"
        result = await self.session.execute(
            select(Strategy).where(
                or_(
                    Strategy.name.like(keyword_pattern),
                    Strategy.description.like(keyword_pattern)
                )
            )
        )
        return list(result.scalars().all())
    
    async def create(self, strategy_data: Dict) -> Strategy:
        """Create a new strategy."""
        strategy = Strategy(**strategy_data)
        self.session.add(strategy)
        await self.session.flush()
        await self.session.refresh(strategy)
        return strategy
    
    async def update(self, strategy_id: int, updates: Dict) -> Optional[Strategy]:
        """Update a strategy."""
        strategy = await self.get_by_id(strategy_id)
        if not strategy:
            return None
        
        for key, value in updates.items():
            if hasattr(strategy, key):
                setattr(strategy, key, value)
        
        strategy.updated_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(strategy)
        return strategy
    
    async def delete(self, strategy_id: int) -> bool:
        """Delete a strategy."""
        strategy = await self.get_by_id(strategy_id)
        if not strategy:
            return False
        
        await self.session.delete(strategy)
        await self.session.flush()
        return True
    
    async def count(self) -> int:
        """Count total strategies in database."""
        result = await self.session.execute(select(Strategy))
        return len(list(result.scalars().all()))
    
    async def exists(self, strategy_id: str) -> bool:
        """Check if a strategy exists by strategy_id."""
        result = await self.session.execute(
            select(Strategy).where(Strategy.strategy_id == strategy_id)
        )
        return result.scalar_one_or_none() is not None
    
    async def seed_strategies(self) -> Dict:
        """
        Seed all 46 strategies and 7 tactics from the registry into the database.
        
        Returns:
            Dict with counts of created, updated, and skipped strategies
        """
        created = 0
        updated = 0
        skipped = 0
        
        # Get all strategies from registry
        all_definitions = list(self.registry._strategies.values())
        
        for definition in all_definitions:
            # Check if strategy already exists
            existing = await self.get_by_strategy_id(definition.strategy_id)
            
            strategy_data = {
                "strategy_id": definition.strategy_id,
                "name": definition.name,
                "category": definition.category,
                "tier": definition.tier,
                "sector": definition.sector,
                "department": definition.department,
                "is_tactic": definition.is_tactic,
                "description": definition.description,
                "parameters": definition.parameters,
                "status": "active",
                "v2_enabled": definition.v2_enabled,
            }
            
            if existing:
                # Update existing strategy
                for key, value in strategy_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
                updated += 1
            else:
                # Create new strategy
                strategy = Strategy(**strategy_data)
                self.session.add(strategy)
                created += 1
        
        await self.session.flush()
        
        logger.info(f"Strategy seed complete: {created} created, {updated} updated, {skipped} skipped")
        
        return {
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "total": created + updated + skipped,
        }
    
    async def get_stats(self) -> Dict:
        """Get database strategy statistics."""
        all_strategies = await self.get_all()
        tactics = await self.get_tactics()
        active = await self.get_active()
        v2_enabled = await self.get_v2_enabled()
        
        # Group by category
        by_category: Dict[str, int] = {}
        by_tier: Dict[str, int] = {}
        by_sector: Dict[str, int] = {}
        by_department: Dict[str, int] = {}
        
        for strategy in all_strategies:
            # Category
            by_category[strategy.category] = by_category.get(strategy.category, 0) + 1
            
            # Tier
            if strategy.tier:
                by_tier[strategy.tier] = by_tier.get(strategy.tier, 0) + 1
            
            # Sector
            if strategy.sector:
                sectors = strategy.sector.split(",")
                for sector in sectors:
                    sector = sector.strip()
                    by_sector[sector] = by_sector.get(sector, 0) + 1
            
            # Department
            if strategy.department:
                by_department[strategy.department] = by_department.get(strategy.department, 0) + 1
        
        return {
            "total_strategies": len(all_strategies) - len(tactics),
            "total_tactics": len(tactics),
            "total": len(all_strategies),
            "active": len(active),
            "v2_enabled": len(v2_enabled),
            "by_category": by_category,
            "by_tier": by_tier,
            "by_sector": by_sector,
            "by_department": by_department,
        }


async def seed_all_strategies(session: AsyncSession) -> Dict:
    """
    Convenience function to seed all strategies into the database.
    
    Usage:
        from app.strategies.repository import seed_all_strategies
        from app.database import get_async_session
        
        async with get_async_session() as session:
            result = await seed_all_strategies(session)
    """
    repository = StrategyRepository(session)
    return await repository.seed_strategies()


__all__ = [
    "StrategyRepository",
    "seed_all_strategies",
]