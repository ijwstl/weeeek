from enum import StrEnum


class Permission(StrEnum):
    DEPARTMENT_READ = "department.read"
    DEPARTMENT_CREATE = "department.create"
    DEPARTMENT_UPDATE = "department.update"
    DEPARTMENT_DELETE = "department.delete"
    DEPARTMENT_MEMBER_MANAGE = "department.member.manage"
    DEPARTMENT_RULE_MANAGE = "department.rule.manage"
    DEPARTMENT_TEMPLATE_MANAGE = "department.template.manage"
    DEPARTMENT_REPORT_VIEW = "department.report.view"
    DEPARTMENT_REPORT_SUMMARY = "department.report.summary"

    PROJECT_READ = "project.read"
    PROJECT_CREATE = "project.create"
    PROJECT_UPDATE = "project.update"
    PROJECT_ARCHIVE = "project.archive"
    PROJECT_MEMBER_MANAGE = "project.member.manage"
    PROJECT_RULE_MANAGE = "project.rule.manage"
    PROJECT_TEMPLATE_MANAGE = "project.template.manage"
    PROJECT_PROGRESS_VIEW = "project.progress.view"
    PROJECT_SUMMARY_VIEW = "project.summary.view"

    REPORT_READ_OWN = "report.read.own"
    REPORT_SUBMIT_OWN = "report.submit.own"
    REPORT_UPDATE_OWN = "report.update.own"
    REPORT_READ_SPACE = "report.read.space"
    REPORT_EXPORT = "report.export"

    TEMPLATE_CREATE = "template.create"
    TEMPLATE_UPDATE = "template.update"
    TEMPLATE_PUBLISH = "template.publish"

    DATASOURCE_MANAGE_OWN = "datasource.manage.own"
    DATASOURCE_PROVIDER_MANAGE = "datasource.provider.manage"

    WORKSPACE_MEMBER_MANAGE = "workspace.member.manage"
    WORKSPACE_ROLE_MANAGE = "workspace.role.manage"
    WORKSPACE_SETTING_MANAGE = "workspace.setting.manage"
    WORKSPACE_AUDIT_VIEW = "workspace.audit.view"

    AI_GENERATE_OWN = "ai.generate.own"
    AI_SUMMARY_SPACE = "ai.summary.space"

    NOTIFICATION_CHANNEL_MANAGE = "notification.channel.manage"
    NOTIFICATION_RULE_MANAGE = "notification.rule.manage"

