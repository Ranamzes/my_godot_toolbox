extends Node

# ==============================================================================
# МЕНЕДЖЕР СЦЕН (Scene Manager)
# ==============================================================================
# Позволяет плавно переключать сцены с затемнением (Fade Out -> Fade In).
#
# Пример использования:
#   SceneManager.change_scene("res://scenes/main_menu.tscn")
# ==============================================================================

var canvas_layer: CanvasLayer
var color_rect: ColorRect
var animation_player: AnimationPlayer

func _ready():
	process_mode = PROCESS_MODE_ALWAYS # Работает даже во время паузы игры
	
	# Программно создаем оверлей затемнения
	canvas_layer = CanvasLayer.new()
	canvas_layer.name = "FadeLayer"
	canvas_layer.layer = 128
	
	color_rect = ColorRect.new()
	color_rect.name = "FadeRect"
	color_rect.color = Color.BLACK
	color_rect.anchors_preset = Control.PRESET_FULL_RECT
	color_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	color_rect.color.a = 0.0
	
	canvas_layer.add_child(color_rect)
	add_child(canvas_layer)
	
	# Настройка анимаций
	animation_player = AnimationPlayer.new()
	animation_player.name = "FadeAnimationPlayer"
	add_child(animation_player)
	
	var library = AnimationLibrary.new()
	
	# Fade Out (прозрачный -> черный)
	var anim_out = Animation.new()
	var track_out = anim_out.add_track(Animation.TYPE_VALUE)
	anim_out.track_set_path(track_out, "FadeLayer/FadeRect:color:a")
	anim_out.track_insert_key(track_out, 0.0, 0.0)
	anim_out.track_insert_key(track_out, 0.3, 1.0)
	library.add_animation("fade_out", anim_out)
	
	# Fade In (черный -> прозрачный)
	var anim_in = Animation.new()
	var track_in = anim_in.add_track(Animation.TYPE_VALUE)
	anim_in.track_set_path(track_in, "FadeLayer/FadeRect:color:a")
	anim_in.track_insert_key(track_in, 0.0, 1.0)
	anim_in.track_insert_key(track_in, 0.3, 0.0)
	library.add_animation("fade_in", anim_in)
	
	animation_player.add_animation_library("", library)

func change_scene(target_scene_path: String):
	color_rect.mouse_filter = Control.MOUSE_FILTER_ALL
	animation_player.play("fade_out")
	await animation_player.animation_finished
	
	var err = get_tree().change_scene_to_file(target_scene_path)
	if err != OK:
		print("[-] SceneManager: Ошибка при смене сцены на: ", target_scene_path, " Код ошибки: ", err)
	
	animation_player.play("fade_in")
	await animation_player.animation_finished
	color_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
