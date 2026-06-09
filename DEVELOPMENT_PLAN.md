# Weeeek MVP Development Plan

## 1. Confirmed Stack

Frontend:

- Vue 3
- TypeScript
- Vite
- Pinia
- Vue Router
- Vue Query
- Naive UI

Backend:

- Python
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic

Storage and async:

- PostgreSQL
- Redis
- Celery

Integrations:

- Feishu OAuth and bot.
- LDAP/AD.
- GitHub.
- GitLab.
- Jira.
- OpenAI-compatible model provider.

## 2. Repository Structure

Recommended structure:

```text
weeeek/
  backend/
    app/
      api/
      core/
      db/
      models/
      schemas/
      services/
      tasks/
      integrations/
      permissions/
      audit/
      notifications/
    alembic/
    tests/
    pyproject.toml
  frontend/
    src/
      api/
      assets/
      components/
      layouts/
      pages/
      router/
      stores/
      styles/
      types/
    package.json
  docker-compose.yml
  REQUIREMENTS.md
  DEVELOPMENT_PLAN.md
```

## 3. Backend Modules

### 3.1 Core

- App settings.
- Database session management.
- Request context.
- Error handling.
- Pagination.
- Encryption utilities.
- Background task configuration.

### 3.2 Auth / Identity

- Feishu OAuth login.
- LDAP login.
- Token issue, refresh, logout.
- Current user/member/workspace API.
- User identity binding.

### 3.3 Workspace / Member / RBAC

- Workspace settings.
- Member management.
- Permission seed data.
- Built-in role seed data.
- Custom role CRUD.
- Role permission assignment.
- Member role assignment with scope.
- `require_permission` dependency/decorator.

### 3.4 Department

- Department tree.
- Department create/update/delete.
- Depth validation.
- Member assignment.
- Department report space initialization.
- Department summary and submission status.

### 3.5 Project Team

- Project team CRUD.
- Member management.
- Project report space initialization.
- Milestones.
- Risks.
- Blockers.
- Archive and restore.

### 3.6 ReportSpace / Rule

- Report space settings.
- Daily/weekly/custom rule management.
- Visibility policy.
- Data source policy.
- Template binding.
- Rule validation.

### 3.7 Template

- Template CRUD.
- Draft schema editing.
- Schema validation.
- Publish immutable versions.
- Template cloning.
- Template version retrieval.

### 3.8 Report

- Generate report instances.
- My tasks.
- My history.
- Draft save.
- Submit.
- Late submit.
- Submission versions.
- Space report listing.
- Submission status.
- Summary and export placeholders.

### 3.9 Data Source

- Workspace integration provider CRUD.
- User data source CRUD.
- Credential encryption.
- Scope management.
- Connection testing.
- GitHub/GitLab/Jira client abstractions.

### 3.10 AI Draft

- Context preview.
- Evidence collection.
- Prompt building.
- OpenAI-compatible provider client.
- Field-based draft generation.
- AI generation run records.
- Fill-empty and overwrite-selected modes.

### 3.11 Notification

- Notification channel plugin interface.
- In-app channel.
- Feishu channel.
- Webhook channel.
- Notification rules.
- Notification events.
- Delivery records.
- Retry handling.

### 3.12 Audit

- Audit decorator.
- Request middleware context.
- Service-level event recording.
- Audit log query API.
- Sensitive metadata filtering.

## 4. Database Implementation Order

Migration 001:

- `users`
- `workspaces`
- `members`
- `user_identities`
- `auth_provider_configs`

Migration 002:

- `permissions`
- `roles`
- `role_permissions`
- `member_role_assignments`
- Seed built-in permissions and roles.

Migration 003:

- `departments`
- `project_teams`
- `project_team_members`
- `project_milestones`
- `project_risks`
- `project_blockers`

Migration 004:

- `report_spaces`
- `report_rules`
- `report_template_bindings`

Migration 005:

- `report_templates`
- `report_template_versions`

Migration 006:

- `report_instances`
- `report_drafts`
- `report_submissions`

Migration 007:

- `integration_providers`
- `user_data_sources`
- `evidence_items`
- `ai_generation_runs`

Migration 008:

- `notification_channels`
- `notification_rules`
- `notification_events`
- `notifications`
- `notification_deliveries`

Migration 009:

- `audit_logs`

## 5. API Milestones

### Milestone A: Foundation

- Backend project scaffold.
- Frontend project scaffold.
- Docker Compose for PostgreSQL and Redis.
- Health check.
- Settings and environment config.
- Database migration pipeline.

Acceptance:

- Backend starts.
- Frontend starts.
- Database migration runs.
- Health endpoint passes.

### Milestone B: Auth And Workspace

- Feishu OAuth placeholder implementation.
- LDAP login implementation.
- Token auth.
- Current user API.
- Workspace bootstrap for private deployment.
- Member model and APIs.

Acceptance:

- User can log in.
- User has current workspace context.
- Private deployment can auto-create default workspace.

### Milestone C: RBAC

- Permission seed.
- Built-in roles.
- Role CRUD.
- Role permissions.
- Member role assignment.
- Permission guard.
- Audit basic hooks.

Acceptance:

- APIs reject missing permissions.
- Scoped department/project permissions can be checked.
- Role permissions are visible in UI data shape.

### Milestone D: Department And Project Basics

- Department tree CRUD.
- Department depth validation.
- Member department assignment.
- ReportSpace auto-create for departments.
- Project team CRUD.
- Project members.
- ReportSpace auto-create for projects.

Acceptance:

- Department tree can be managed.
- User can belong to exactly one department.
- Project can include cross-department members.

### Milestone E: Templates

- Template CRUD.
- Draft editing.
- Schema validation.
- Publish version.
- Template binding.
- Inheritance/override behavior for departments.
- Table field schema support.

Acceptance:

- Department can bind daily/weekly templates.
- Template version snapshots are immutable.
- Table fields can be configured.

### Milestone F: Report Flow

- Report rule CRUD.
- Report instance generation task.
- My tasks.
- Draft save.
- Submit.
- Late submit.
- Submission versions.
- Report visibility checks.
- Department/project submission status.

Acceptance:

- Member can fill and submit reports.
- Lead/admin can see allowed submitted reports.
- Drafts remain private.
- Same-department/member visibility works.

### Milestone G: Notifications

- Notification channel plugin interface.
- In-app notification.
- Feishu notification.
- Webhook notification.
- Notification rules.
- Reminder task.
- Overdue task.

Acceptance:

- Reminder events create notifications.
- In-app and Feishu deliveries can be tracked.
- Webhook channel can be tested.

### Milestone H: Data Sources

- Integration provider APIs.
- Personal data source APIs.
- Credential encryption.
- GitHub/GitLab clients.
- Jira client.
- Scope config.
- Connection testing.

Acceptance:

- User can bind Git/Jira.
- Backend can fetch MVP evidence for a period.
- Failed auth is visible to the user.

### Milestone I: AI Draft

- AI provider config.
- Context preview.
- Evidence collection.
- AI generation task.
- Field-based output mapping.
- Fill-empty behavior.
- AI generation records.

Acceptance:

- User can generate a draft from selected sources.
- AI cannot use unauthorized sources.
- Generated content does not auto-submit.

### Milestone J: Frontend Completion

- App layout.
- Login/workspace flow.
- Dashboard.
- Report filling page.
- Department config page.
- Template editor.
- Project team pages.
- Data source and AI settings page.
- Report center.
- Role/permission settings.
- Audit log page.

Acceptance:

- End-to-end reporting loop works from UI.
- Core pages match the agreed product direction.

## 6. Frontend Page Plan

### 6.1 App Shell

- Left sidebar navigation.
- Top workspace/user bar.
- Notification entry.
- Permission-aware menu visibility.

### 6.2 Dashboard

- My pending reports.
- Overdue reports.
- Recent submissions.
- Participating projects.
- Team submission summary when user has scope permission.

### 6.3 Report Filling Page

- Report metadata header.
- Grouped template fields.
- Table field row editing.
- AI assistant side panel.
- Source selection.
- Save draft.
- Preview.
- Submit.

### 6.4 Department Configuration

- Department tree.
- Basic information.
- Reporting rules.
- Template binding/inheritance.
- Permission and visibility settings.
- Members.

### 6.5 Template Editor

- Group and field tree.
- Canvas preview.
- Field property panel.
- Table column editor.
- Validate.
- Publish.

### 6.6 Project Team

- Project list.
- Project detail.
- Members.
- Progress rules.
- Progress reports.
- Milestones.
- Risks.
- Blockers.
- Archive.

### 6.7 Data Source And AI Settings

- GitHub/GitLab/Jira connection list.
- Test connection.
- Edit scopes.
- AI preferences.
- Authorization and generation records.

### 6.8 Settings

- Workspace settings.
- Members.
- Roles and permission matrix.
- Auth provider configs.
- Integration providers.
- Notification channels.
- AI provider configs.
- Audit logs.

## 7. Celery Tasks

Tasks:

- `report.generate_instances`
- `report.mark_overdue`
- `notification.create_event`
- `notification.dispatch`
- `datasource.fetch_git`
- `datasource.fetch_jira`
- `ai.generate_report_draft`
- `audit.write_log` optional

Scheduling:

- Periodic report instance generation.
- Periodic overdue scanning.
- Reminder dispatch based on report rules.

## 8. Security Requirements

- Encrypt all credentials at rest.
- Never return credential plaintext to frontend.
- Never log tokens.
- Always filter workspace by context.
- Audit sensitive operations.
- AI must not receive tokens or code diffs.
- AI must only use data the acting user can access.
- Report drafts are private.
- Workspace admins cannot view all submitted report bodies by default.

## 9. Testing Plan

Backend tests:

- Permission guard and scope coverage.
- Department depth validation.
- Report rule period calculation.
- Template schema validation.
- Template version immutability.
- Report draft/submit/late submit flow.
- Report visibility rules.
- Data source credential encryption.
- AI context permission filtering.
- Notification channel plugin dispatch.
- Audit decorator.

Frontend tests:

- Permission-aware navigation.
- Report filling form rendering.
- Table field editing.
- Template editor schema operations.
- Data source state rendering.
- Role permission matrix.

Integration tests:

- Login to submit report flow.
- Department lead view flow.
- Project progress flow.
- AI draft generation with mocked Git/Jira.
- Notification delivery with mocked Feishu/Webhook.

## 10. MVP Build Order

Recommended execution:

1. Scaffold backend and frontend.
2. Add database, migrations, settings, Docker Compose.
3. Implement auth/workspace/member.
4. Implement RBAC.
5. Implement departments and report spaces.
6. Implement templates.
7. Implement report rules and report flow.
8. Implement notifications.
9. Implement project teams.
10. Implement data sources.
11. Implement AI drafts.
12. Complete audit logs and settings pages.
13. Polish frontend UX and run end-to-end tests.
