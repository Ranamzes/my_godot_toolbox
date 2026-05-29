extends Node

# ==============================================================================
# МЕНЕДЖЕР ЗВУКА (Sound Manager)
# ==============================================================================
# Позволяет быстро проигрывать SFX и управлять фоновой музыкой.
# Использует пул плееров, чтобы звуки не прерывали друг друга.
#
# Пример использования:
#   SoundManager.play_sfx(preload("res://assets/sounds/jump.wav"))
#   SoundManager.play_music(preload("res://assets/music/theme.ogg"))
# ==============================================================================

var music_player: AudioStreamPlayer
var sfx_pool: Array[AudioStreamPlayer] = []
var max_sfx_players: int = 12

func _ready():
	process_mode = PROCESS_MODE_ALWAYS # Звуки играют даже при паузе
	
	# Инициализируем плеер музыки
	music_player = AudioStreamPlayer.new()
	music_player.name = "MusicPlayer"
	add_child(music_player)
	
	# Инициализируем пул звуковых эффектов
	for i in range(max_sfx_players):
		var player = AudioStreamPlayer.new()
		player.name = "SFXPlayer_" + str(i)
		add_child(player)
		sfx_pool.append(player)

## Воспроизвести звуковой эффект с легким варьированием тональности (для реалистичности)
func play_sfx(stream: AudioStream, pitch_randomness: float = 0.08) -> AudioStreamPlayer:
	if not stream:
		return null
		
	# Ищем свободный плеер
	for player in sfx_pool:
		if not player.playing:
			player.stream = stream
			if pitch_randomness > 0.0:
				player.pitch_scale = randf_range(1.0 - pitch_randomness, 1.0 + pitch_randomness)
			else:
				player.pitch_scale = 1.0
			player.play()
			return player
			
	# Если свободного нет, перехватываем первый занятый
	var fallback_player = sfx_pool[0]
	fallback_player.stream = stream
	fallback_player.pitch_scale = 1.0
	fallback_player.play()
	return fallback_player

## Воспроизвести фоновую музыку
func play_music(stream: AudioStream, fade_out_time: float = 0.4) -> void:
	if not stream:
		return
		
	if music_player.playing and music_player.stream == stream:
		return # Музыка уже играет
		
	if music_player.playing and fade_out_time > 0.0:
		var tween = create_tween()
		tween.tween_property(music_player, "volume_db", -80.0, fade_out_time)
		await tween.finished
		
	music_player.stream = stream
	music_player.volume_db = 0.0
	music_player.play()

## Остановить воспроизведение музыки
func stop_music(fade_out_time: float = 0.4) -> void:
	if not music_player.playing:
		return
		
	if fade_out_time > 0.0:
		var tween = create_tween()
		tween.tween_property(music_player, "volume_db", -80.0, fade_out_time)
		await tween.finished
		
	music_player.stop()
	music_player.volume_db = 0.0
