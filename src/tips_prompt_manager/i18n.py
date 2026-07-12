"""Bilingual UI text and small local language setting."""

from __future__ import annotations

import json

from .paths import settings_path


LANGUAGES = {"zh", "en"}

TEXT: dict[str, dict[str, str]] = {
    "zh": {
        "app_title": "TIPS 提示词管理器",
        "subtitle": "离线管理提示词、分类、搜索和复制",
        "new": "新建",
        "save": "保存",
        "copy": "复制内容",
        "delete": "删除",
        "category": "分类",
        "all_categories": "全部分类",
        "default_category": "未分类",
        "add_category": "新增分类",
        "rename": "重命名",
        "delete_category": "删除分类",
        "search": "搜索",
        "clear": "清空",
        "prompt_list": "提示词列表",
        "title": "标题",
        "content": "提示词内容",
        "basic_info": "基础信息",
        "updated_at": "更新时间：{value}",
        "ready": "就绪",
        "no_search": "无搜索",
        "count": "{count} 条",
        "content_matches": "内容匹配 {count} 处",
        "editing": "正在编辑：{title}",
        "new_prompt": "新建提示词",
        "saved": "已保存",
        "copied": "内容已复制到剪贴板",
        "deleted_prompt": "已删除提示词",
        "added_category": "已添加分类：{name}",
        "renamed_category": "已重命名分类：{name}",
        "deleted_category": "已删除分类",
        "language": "English",
        "about": "关于",
        "about_text": "TIPS 提示词管理器 v{version}\n\n作者：{author}\n邮箱：{email}\n主页：{home}\nGitHub：{github}\n\n本工具离线运行，使用 SQLite 保存在本机。\n密码哈希用于启动验证，数据库文件本身未加密。\n发布包未进行数字签名。",
        "setup_title": "首次使用 - 设置密码",
        "setup_intro": "请为 TIPS 提示词管理器设置本地密码",
        "password": "密码",
        "confirm_password": "确认密码",
        "local_password_note": "密码哈希只保存在本机，不会联网。",
        "password_too_short_title": "密码太短",
        "password_too_short": "密码至少需要 4 位。",
        "password_mismatch_title": "密码不一致",
        "password_mismatch": "两次输入的密码不一致。",
        "verify_title": "密码验证",
        "verify_intro": "本次开机首次打开需要输入密码",
        "too_many_attempts_title": "验证失败",
        "too_many_attempts": "密码错误次数过多，应用将退出。",
        "attempts_left": "密码错误，还可尝试 {count} 次。",
        "category_name": "分类名称",
        "empty_name_title": "名称不能为空",
        "empty_name": "请输入分类名称。",
        "missing_title_title": "缺少标题",
        "missing_title": "请输入提示词标题。",
        "missing_content_title": "缺少内容",
        "missing_content": "请输入提示词内容。",
        "invalid_category_title": "分类无效",
        "invalid_category": "请选择有效分类。",
        "empty_copy_title": "没有内容",
        "empty_copy": "当前没有可复制的提示词内容。",
        "confirm_delete_title": "确认删除",
        "confirm_delete": "确定删除“{title}”吗？",
        "category_exists_title": "分类已存在",
        "category_exists": "这个分类名称已经存在。",
        "choose_category_title": "请选择分类",
        "choose_category": "请先在顶部分类筛选中选择一个具体分类。",
        "system_category_title": "系统分类",
        "system_category_rename": "默认分类不能重命名。",
        "system_category_delete": "默认分类不能删除。",
        "confirm_delete_category": "确定删除分类“{name}”吗？其中的提示词会移动到“{fallback}”。",
    },
    "en": {
        "app_title": "TIPS Prompt Manager",
        "subtitle": "Offline prompt storage, categories, search, and copy",
        "new": "New",
        "save": "Save",
        "copy": "Copy",
        "delete": "Delete",
        "category": "Category",
        "all_categories": "All categories",
        "default_category": "Uncategorized",
        "add_category": "Add category",
        "rename": "Rename",
        "delete_category": "Delete category",
        "search": "Search",
        "clear": "Clear",
        "prompt_list": "Prompts",
        "title": "Title",
        "content": "Prompt content",
        "basic_info": "Details",
        "updated_at": "Updated: {value}",
        "ready": "Ready",
        "no_search": "No search",
        "count": "{count} item(s)",
        "content_matches": "{count} content match(es)",
        "editing": "Editing: {title}",
        "new_prompt": "New prompt",
        "saved": "Saved",
        "copied": "Copied to clipboard",
        "deleted_prompt": "Prompt deleted",
        "added_category": "Category added: {name}",
        "renamed_category": "Category renamed: {name}",
        "deleted_category": "Category deleted",
        "language": "中文",
        "about": "About",
        "about_text": "TIPS Prompt Manager v{version}\n\nAuthor: {author}\nEmail: {email}\nHomepage: {home}\nGitHub: {github}\n\nRuns offline and stores data locally with SQLite.\nThe password hash protects app launch; the database file itself is not encrypted.\nRelease binaries are not digitally signed.",
        "setup_title": "First run - Set password",
        "setup_intro": "Set a local password for TIPS Prompt Manager",
        "password": "Password",
        "confirm_password": "Confirm password",
        "local_password_note": "Only a local password hash is stored. No network is used.",
        "password_too_short_title": "Password too short",
        "password_too_short": "Use at least 4 characters.",
        "password_mismatch_title": "Passwords do not match",
        "password_mismatch": "The two passwords do not match.",
        "verify_title": "Password verification",
        "verify_intro": "Enter your password the first time this app opens after boot",
        "too_many_attempts_title": "Verification failed",
        "too_many_attempts": "Too many failed attempts. The app will exit.",
        "attempts_left": "Incorrect password. {count} attempt(s) left.",
        "category_name": "Category name",
        "empty_name_title": "Name required",
        "empty_name": "Enter a category name.",
        "missing_title_title": "Title required",
        "missing_title": "Enter a prompt title.",
        "missing_content_title": "Content required",
        "missing_content": "Enter prompt content.",
        "invalid_category_title": "Invalid category",
        "invalid_category": "Choose a valid category.",
        "empty_copy_title": "No content",
        "empty_copy": "There is no prompt content to copy.",
        "confirm_delete_title": "Confirm delete",
        "confirm_delete": "Delete \"{title}\"?",
        "category_exists_title": "Category exists",
        "category_exists": "A category with this name already exists.",
        "choose_category_title": "Choose a category",
        "choose_category": "Choose a specific category from the filter first.",
        "system_category_title": "System category",
        "system_category_rename": "The default category cannot be renamed.",
        "system_category_delete": "The default category cannot be deleted.",
        "confirm_delete_category": "Delete category \"{name}\"? Its prompts will move to \"{fallback}\".",
    },
}


def normalize_language(language: str | None) -> str:
    return language if language in LANGUAGES else "zh"


def load_language() -> str:
    try:
        data = json.loads(settings_path().read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return "zh"
    return normalize_language(data.get("language"))


def save_language(language: str) -> None:
    path = settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"language": normalize_language(language)}
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)
