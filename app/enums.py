import enum

# Статус задачі
class TaskStatus(str, enum.Enum):
    TODO = 'TODO'
    IN_PROGRESS = 'In progress'
    DONE = 'Done'

# Пріоритет задачі
class TaskPriority(str, enum.Enum):
    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'

# Роль користувача
class UserRole(str, enum.Enum):
    ADMIN = 'Admin'
    USER = 'User'