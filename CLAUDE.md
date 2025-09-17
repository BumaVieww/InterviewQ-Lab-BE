CLAUDE.md (정리된 버전)

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

📂 Directory Structure
api/
 ├─ schemas/
 ├─ depends/
 └─ routers/

app/
 └─ domain/ (ex: user, question)
     ├─ service/
     ├─ repository/
     ├─ model/ (entity)
     └─ 기타 모듈

core/

🗄️ Database & Models

모델 정의는 아래 DDL을 기준으로 합니다.
DDL을 참고하여 초기 스키마, 마이그레이션, 시드, 그리고 기본 CRUD API가 동작하는 **최소 기능 제품(MVP)**을 구성하세요.

생성 순서 (FK 무결성 보장)
user → company → position → question → answer 
→ answer_comment → goal_company → user_position 
→ company_analyze → keywords_by_position

⚙️ Application Stack

Framework: FastAPI

ORM: SQLAlchemy

Migration: Alembic

API Design Tool: Apidog MCP (모든 API 엔드포인트 정의 및 테스트 자동화에 활용)

📌 API Guidelines

Pagination: 모든 조회 API는 Cursor 기반 페이지네이션을 사용합니다.

Query Parameters: cursor_id, size

Performance: ORM 사용 시 N+1 문제를 방지하기 위해 selectinload 또는 이에 준하는 최적화를 기본 적용합니다.

📝 Additional Notes

DDL에 명시된 FK, PK, 제약 조건을 Source of Truth로 삼습니다.

불명확한 스펙(예: ENUM 값 확장)은 보수적으로 구현하고 TODO 주석을 남깁니다.

Apidog MCP를 통해 설계된 스펙은 곧바로 FastAPI Router에 반영할 수 있도록 관리합니다.