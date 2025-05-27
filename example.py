from filesave import FileSaveSystem  # Importing the module

# Initializing the file system for storing configuration settings
config_system = FileSaveSystem("example.txt", system_type="read-write", encoded=False)

# Setting up the structure
config_system.new_group("UserPreferences")
config_system.new_subgroup("Display", "UserPreferences")
config_system.new_item("Brightness", 80, "UserPreferences", "Display")
config_system.new_item("Theme", "Dark", "UserPreferences", "Display")

config_system.new_subgroup("Sound", "UserPreferences")
config_system.new_item("Volume", 50, "UserPreferences", "Sound")
config_system.new_item("Muted", False, "UserPreferences", "Sound")

print(config_system.data)

# Saving the settings to the file
config_system.save()

# Retrieving stored values
theme_setting = config_system.item_content("UserPreferences", "Display", "Theme")
print(f"Selected Theme: {theme_setting}")

sound_settings = config_system.subgroup_content("UserPreferences", "Sound")
print(f"Sound Preferences: {sound_settings}")