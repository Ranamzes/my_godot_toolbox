extends Node

# ==============================================================================
# ГЛОБАЛЬНАЯ ШИНА СОБЫТИЙ (Event Bus / Signal Bus)
# ==============================================================================
# Используется для связи между слабо связанными компонентами.
#
# Пример подписки в принимающем скрипте (например, UI здоровья):
#   func _ready():
#       EventBus.player_health_changed.connect(_on_health_changed)
#
#   func _on_health_changed(new_hp, max_hp):
#       hp_bar.value = new_hp
#
# Пример вызова в отправляющем скрипте (например, игрок):
#   func take_damage(amount):
#       health -= amount
#       EventBus.player_health_changed.emit(health, max_health)
# ==============================================================================

# Общие игровые сигналы
signal game_started
signal game_paused(is_paused: bool)
signal game_over(victory: bool)

# Игрок
signal player_spawned(player_node: Node2D)
signal player_died
signal player_health_changed(current_health: int, max_health: int)

# Уровни и прогресс
signal level_completed(level_index: int)
signal score_updated(new_score: int)
