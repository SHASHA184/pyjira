import enum

# Статус задачі
class TaskStatus(str, enum.Enum):
    TODO = 'todo'
    IN_PROGRESS = 'in progress'
    DONE = 'done'

# Пріоритет задачі
class TaskPriority(str, enum.Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'

# Роль користувача
class UserRole(str, enum.Enum):
    ADMIN = 'admin'
    USER = 'user'
    MANAGER = 'manager'
