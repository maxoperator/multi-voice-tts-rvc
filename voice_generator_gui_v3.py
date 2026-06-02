import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import asyncio
import edge_tts
import os
import zipfile
import threading
import time
import json
from collections import defaultdict

# --- БАЗА ДАННЫХ ЯЗЫКОВ ---
BASE_LANGS = {
    'af': {'ru': 'Африкаанс', 'en': 'Afrikaans'},
    'am': {'ru': 'Амхарский', 'en': 'Amharic'},
    'ar': {'ru': 'Арабский', 'en': 'Arabic'},
    'az': {'ru': 'Азербайджанский', 'en': 'Azerbaijani'},
    'bg': {'ru': 'Болгарский', 'en': 'Bulgarian'},
    'bn': {'ru': 'Бенгальский', 'en': 'Bengali'},
    'bs': {'ru': 'Боснийский', 'en': 'Bosnian'},
    'ca': {'ru': 'Каталанский', 'en': 'Catalan'},
    'cs': {'ru': 'Чешский', 'en': 'Czech'},
    'cy': {'ru': 'Валлийский', 'en': 'Welsh'},
    'da': {'ru': 'Датский', 'en': 'Danish'},
    'de': {'ru': 'Немецкий', 'en': 'German'},
    'el': {'ru': 'Греческий', 'en': 'Greek'},
    'en': {'ru': 'Английский', 'en': 'English'},
    'es': {'ru': 'Испанский', 'en': 'Spanish'},
    'et': {'ru': 'Эстонский', 'en': 'Estonian'},
    'fa': {'ru': 'Персидский', 'en': 'Persian'},
    'fi': {'ru': 'Финский', 'en': 'Finnish'},
    'fil': {'ru': 'Филиппинский', 'en': 'Filipino'},
    'fr': {'ru': 'Французский', 'en': 'French'},
    'ga': {'ru': 'Ирландский', 'en': 'Irish'},
    'gl': {'ru': 'Галисийский', 'en': 'Galician'},
    'gu': {'ru': 'Гуджарати', 'en': 'Gujarati'},
    'he': {'ru': 'Иврит', 'en': 'Hebrew'},
    'hi': {'ru': 'Хинди', 'en': 'Hindi'},
    'hr': {'ru': 'Хорватский', 'en': 'Croatian'},
    'hu': {'ru': 'Венгерский', 'en': 'Hungarian'},
    'id': {'ru': 'Индонезийский', 'en': 'Indonesian'},
    'is': {'ru': 'Исландский', 'en': 'Icelandic'},
    'it': {'ru': 'Итальянский', 'en': 'Italian'},
    'ja': {'ru': 'Японский', 'en': 'Japanese'},
    'jv': {'ru': 'Яванский', 'en': 'Javanese'},
    'ka': {'ru': 'Грузинский', 'en': 'Georgian'},
    'kk': {'ru': 'Казахский', 'en': 'Kazakh'},
    'km': {'ru': 'Кхмерский', 'en': 'Khmer'},
    'kn': {'ru': 'Каннада', 'en': 'Kannada'},
    'ko': {'ru': 'Корейский', 'en': 'Korean'},
    'lo': {'ru': 'Лаосский', 'en': 'Lao'},
    'lt': {'ru': 'Литовский', 'en': 'Lithuanian'},
    'lv': {'ru': 'Латышский', 'en': 'Latvian'},
    'mk': {'ru': 'Македонский', 'en': 'Macedonian'},
    'ml': {'ru': 'Малаялам', 'en': 'Malayalam'},
    'mn': {'ru': 'Монгольский', 'en': 'Mongolian'},
    'mr': {'ru': 'Маратхи', 'en': 'Marathi'},
    'ms': {'ru': 'Малайский', 'en': 'Malay'},
    'mt': {'ru': 'Мальтийский', 'en': 'Maltese'},
    'my': {'ru': 'Бирманский', 'en': 'Burmese'},
    'nb': {'ru': 'Норвежский', 'en': 'Norwegian'},
    'ne': {'ru': 'Непальский', 'en': 'Nepali'},
    'nl': {'ru': 'Нидерландский', 'en': 'Dutch'},
    'pl': {'ru': 'Польский', 'en': 'Polish'},
    'ps': {'ru': 'Пушту', 'en': 'Pashto'},
    'pt': {'ru': 'Португальский', 'en': 'Portuguese'},
    'ro': {'ru': 'Румынский', 'en': 'Romanian'},
    'ru': {'ru': 'Русский', 'en': 'Russian'},
    'si': {'ru': 'Сингальский', 'en': 'Sinhala'},
    'sk': {'ru': 'Словацкий', 'en': 'Slovak'},
    'sl': {'ru': 'Словенский', 'en': 'Slovenian'},
    'so': {'ru': 'Сомалийский', 'en': 'Somali'},
    'sq': {'ru': 'Албанский', 'en': 'Albanian'},
    'sr': {'ru': 'Сербский', 'en': 'Serbian'},
    'su': {'ru': 'Сунданский', 'en': 'Sundanese'},
    'sv': {'ru': 'Шведский', 'en': 'Swedish'},
    'sw': {'ru': 'Суахили', 'en': 'Swahili'},
    'ta': {'ru': 'Тамильский', 'en': 'Tamil'},
    'te': {'ru': 'Телугу', 'en': 'Telugu'},
    'th': {'ru': 'Тайский', 'en': 'Thai'},
    'tr': {'ru': 'Турецкий', 'en': 'Turkish'},
    'uk': {'ru': 'Украинский', 'en': 'Ukrainian'},
    'ur': {'ru': 'Урду', 'en': 'Urdu'},
    'uz': {'ru': 'Узбекский', 'en': 'Uzbek'},
    'vi': {'ru': 'Вьетнамский', 'en': 'Vietnamese'},
    'zh': {'ru': 'Китайский', 'en': 'Chinese'},
    'zu': {'ru': 'Зулу', 'en': 'Zulu'}
}

# --- БАЗА РЕГИОНОВ ---
REGIONS = {
    'US': {'ru': 'США', 'en': 'USA'},
    'GB': {'ru': 'Великобритания', 'en': 'UK'},
    'AU': {'ru': 'Австралия', 'en': 'Australia'},
    'CA': {'ru': 'Канада', 'en': 'Canada'},
    'IN': {'ru': 'Индия', 'en': 'India'},
    'CN': {'ru': 'Материковый Китай', 'en': 'Mainland China'},
    'TW': {'ru': 'Тайвань', 'en': 'Taiwan'},
    'HK': {'ru': 'Гонконг', 'en': 'Hong Kong'},
    'ES': {'ru': 'Испания', 'en': 'Spain'},
    'MX': {'ru': 'Мексика', 'en': 'Mexico'},
    'BR': {'ru': 'Бразилия', 'en': 'Brazil'},
    'PT': {'ru': 'Португалия', 'en': 'Portugal'},
    'FR': {'ru': 'Франция', 'en': 'France'},
    'DE': {'ru': 'Германия', 'en': 'Germany'},
    'RU': {'ru': 'Россия', 'en': 'Russia'},
    'UA': {'ru': 'Украина', 'en': 'Ukraine'},
    'LK': {'ru': 'Шри-Ланка', 'en': 'Sri Lanka'},
    'JP': {'ru': 'Япония', 'en': 'Japan'},
    'AR': {'ru': 'Аргентина', 'en': 'Argentina'},
    'BO': {'ru': 'Боливия', 'en': 'Bolivia'},
    'CL': {'ru': 'Чили', 'en': 'Chile'},
    'CO': {'ru': 'Колумбия', 'en': 'Colombia'},
    'CR': {'ru': 'Коста-Рика', 'en': 'Costa Rica'},
    'CU': {'ru': 'Куба', 'en': 'Cuba'},
    'DO': {'ru': 'Доминикана', 'en': 'Dominican Republic'},
    'EC': {'ru': 'Эквадор', 'en': 'Ecuador'},
    'GQ': {'ru': 'Экв. Гвинея', 'en': 'Equatorial Guinea'},
    'GT': {'ru': 'Гватемала', 'en': 'Guatemala'},
    'HN': {'ru': 'Гондурас', 'en': 'Honduras'},
    'NI': {'ru': 'Никарагуа', 'en': 'Nicaragua'},
    'PA': {'ru': 'Панама', 'en': 'Panama'},
    'PE': {'ru': 'Перу', 'en': 'Peru'},
    'PR': {'ru': 'Пуэрто-Рико', 'en': 'Puerto Rico'},
    'PY': {'ru': 'Парагвай', 'en': 'Paraguay'},
    'SV': {'ru': 'Сальвадор', 'en': 'El Salvador'},
    'UY': {'ru': 'Уругвай', 'en': 'Uruguay'},
    'VE': {'ru': 'Венесуэла', 'en': 'Venezuela'},
    'DZ': {'ru': 'Алжир', 'en': 'Algeria'},
    'BH': {'ru': 'Бахрейн', 'en': 'Bahrain'},
    'EG': {'ru': 'Египет', 'en': 'Egypt'},
    'IQ': {'ru': 'Ирак', 'en': 'Iraq'},
    'JO': {'ru': 'Иордания', 'en': 'Jordan'},
    'KW': {'ru': 'Кувейт', 'en': 'Kuwait'},
    'LB': {'ru': 'Ливан', 'en': 'Lebanon'},
    'LY': {'ru': 'Ливия', 'en': 'Libya'},
    'MA': {'ru': 'Марокко', 'en': 'Morocco'},
    'OM': {'ru': 'Оман', 'en': 'Oman'},
    'QA': {'ru': 'Катар', 'en': 'Qatar'},
    'SA': {'ru': 'Сауд. Аравия', 'en': 'Saudi Arabia'},
    'SY': {'ru': 'Сирия', 'en': 'Syria'},
    'TN': {'ru': 'Тунис', 'en': 'Tunisia'},
    'YE': {'ru': 'Йемен', 'en': 'Yemen'},
    'AE': {'ru': 'ОАЭ', 'en': 'UAE'},
    'KE': {'ru': 'Кения', 'en': 'Kenya'},
    'NG': {'ru': 'Нигерия', 'en': 'Nigeria'},
    'ZA': {'ru': 'ЮАР', 'en': 'South Africa'},
    'TZ': {'ru': 'Танзания', 'en': 'Tanzania'},
    'IE': {'ru': 'Ирландия', 'en': 'Ireland'},
    'NZ': {'ru': 'Новая Зеландия', 'en': 'New Zealand'},
    'PH': {'ru': 'Филиппины', 'en': 'Philippines'},
    'SG': {'ru': 'Сингапур', 'en': 'Singapore'},
    'BE': {'ru': 'Бельгия', 'en': 'Belgium'},
    'CH': {'ru': 'Швейцария', 'en': 'Switzerland'},
    'AT': {'ru': 'Австрия', 'en': 'Austria'},
    'MY': {'ru': 'Малайзия', 'en': 'Malaysia'}
}

DEFAULT_REGIONS = {
    'en': 'US',
    'es': 'ES',
    'ar': 'SA',
    'zh': 'CN',
    'pt': 'BR',
    'fr': 'FR',
    'de': 'DE',
    'ru': 'RU',
    'it': 'IT',
    'ja': 'JP',
    'ko': 'KR',
    'nl': 'NL',
    'pl': 'PL',
    'tr': 'TR',
    'uk': 'UA',
    'si': 'LK'
}

UI_LANGUAGES = ['ru', 'en', 'uk', 'es', 'de', 'fr', 'pt', 'zh', 'ja', 'ar']

# ПОЛНЫЙ СЛОВАРЬ ПЕРЕВОДОВ ИНТЕРФЕЙСА (Построчный для 100% защиты от багов)
INTERNAL_FALLBACK_LOCALES = {
    "ru": {
        "app_title": "Microsoft Edge TTS - Комбайн генерации",
        "text_label": "Текст для озвучки:",
        "btn_load": "📂 Загрузить из .txt",
        "btn_clear": "🗑 Очистить",
        "settings_frame": " Настройки генерации ",
        "lang_label": "Язык:",
        "region_label": "Регион/Диалект:",
        "gender_label": "Пол голоса:",
        "gender_all": "Любой",
        "gender_male": "Мужской",
        "gender_female": "Женский",
        "voice_label": "Голос:",
        "chars_label": "Символов в фрагменте:",
        "parallel_label": "Параллельные пакеты:",
        "status_ready": "Готов к работе",
        "status_loading_voices": "Подключение к серверам Microsoft... Загрузка голосов...",
        "btn_start": "Сгенерировать и сохранить в ZIP",
        "msg_warning_title": "Внимание",
        "msg_no_text": "Пожалуйста, введите текст для озвучки.",
        "msg_save_title": "Сохранить архив как...",
        "status_calc": "Осталось: вычисление...",
        "status_split": "Текст разбит на {total} фрагментов. Начинаю озвучку...",
        "status_progress": "Готово фрагментов: {done} из {total}...",
        "status_zip": "Сборка аудиофайлов в один ZIP-архив...",
        "status_zip_eta": "Осталось: архивация...",
        "status_done": "Все готово! Архив успешно сохранен.",
        "eta_left": "Осталось: {mins}:{secs}",
        "msg_success_title": "Успех",
        "msg_success_text": "Архив успешно создан:\n{path}",
        "msg_error_title": "Ошибка",
        "msg_error_zip": "Критическая ошибка создания архива: {err}"
    },
    "en": {
        "app_title": "Microsoft Edge TTS - Generator",
        "text_label": "Text to synthesize:",
        "btn_load": "📂 Load from .txt",
        "btn_clear": "🗑 Clear",
        "settings_frame": " Generation Settings ",
        "lang_label": "Language:",
        "region_label": "Region/Dialect:",
        "gender_label": "Voice Gender:",
        "gender_all": "Any",
        "gender_male": "Male",
        "gender_female": "Female",
        "voice_label": "Voice:",
        "chars_label": "Characters per chunk:",
        "parallel_label": "Parallel tasks:",
        "status_ready": "Ready to work",
        "status_loading_voices": "Connecting to Microsoft servers... Loading voices...",
        "btn_start": "Generate and Save to ZIP",
        "msg_warning_title": "Warning",
        "msg_no_text": "Please enter text to synthesize.",
        "msg_save_title": "Save archive as...",
        "status_calc": "ETA: calculating...",
        "status_split": "Text split into {total} chunks. Starting synthesis...",
        "status_progress": "Completed chunks: {done} of {total}...",
        "status_zip": "Assembling audio files into a ZIP archive...",
        "status_zip_eta": "ETA: archiving...",
        "status_done": "All done! Archive successfully saved.",
        "eta_left": "ETA: {mins}:{secs}",
        "msg_success_title": "Success",
        "msg_success_text": "Archive successfully created:\n{path}",
        "msg_error_title": "Error",
        "msg_error_zip": "Critical error creating archive: {err}"
    },
    "uk": {
        "app_title": "Microsoft Edge TTS - Комбайн генерації",
        "text_label": "Текст для озвучення:",
        "btn_load": "📂 Завантажити з .txt",
        "btn_clear": "🗑 Очистити",
        "settings_frame": " Налаштування генерації ",
        "lang_label": "Мова:",
        "region_label": "Регіон/Діалект:",
        "gender_label": "Стать голосу:",
        "gender_all": "Будь-яка",
        "gender_male": "Чоловічий",
        "gender_female": "Жіночий",
        "voice_label": "Голос:",
        "chars_label": "Символів у фрагменті:",
        "parallel_label": "Паралельні пакети:",
        "status_ready": "Готовий до роботи",
        "status_loading_voices": "Завантаження голосів...",
        "btn_start": "Згенерувати та зберегти в ZIP",
        "msg_warning_title": "Увага",
        "msg_no_text": "Будь ласка, введіть текст для озвучення.",
        "msg_save_title": "Зберегти архів як...",
        "status_calc": "Залишилось: обчислення...",
        "status_split": "Текст розбитий на {total} фрагментів. Починаю озвучення...",
        "status_progress": "Готово фрагментів: {done} з {total}...",
        "status_zip": "Збирання аудіофайлів в один ZIP-архів...",
        "status_zip_eta": "Залишилось: архівація...",
        "status_done": "Все готово! Архів успішно збережено.",
        "eta_left": "Залишилось: {mins}:{secs}",
        "msg_success_title": "Успіх",
        "msg_success_text": "Архів успішно створено:\n{path}",
        "msg_error_title": "Помилка",
        "msg_error_zip": "Критична помилка створення архіву: {err}"
    },
    "es": {
        "app_title": "Microsoft Edge TTS - Generador",
        "text_label": "Texto para sintetizar:",
        "btn_load": "📂 Cargar desde .txt",
        "btn_clear": "🗑 Limpiar",
        "settings_frame": " Configuración de generación ",
        "lang_label": "Idioma:",
        "region_label": "Región/Dialecto:",
        "gender_label": "Género de voz:",
        "gender_all": "Cualquiera",
        "gender_male": "Masculino",
        "gender_female": "Femenino",
        "voice_label": "Voz:",
        "chars_label": "Caracteres por fragmento:",
        "parallel_label": "Paquetes paralelos:",
        "status_ready": "Listo para trabajar",
        "status_loading_voices": "Cargando voces...",
        "btn_start": "Generar y guardar en ZIP",
        "msg_warning_title": "Advertencia",
        "msg_no_text": "Por favor, introduce el texto para sintetizar.",
        "msg_save_title": "Guardar archivo como...",
        "status_calc": "Restante: calculando...",
        "status_split": "Texto dividido en {total} fragmentos. Iniciando síntesis...",
        "status_progress": "Fragmentos listos: {done} de {total}...",
        "status_zip": "Ensamblando archivos de audio en un archivo ZIP...",
        "status_zip_eta": "Restante: archivando...",
        "status_done": "¡Todo listo! Archivo guardado con éxito.",
        "eta_left": "Restante: {mins}:{secs}",
        "msg_success_title": "Éxito",
        "msg_success_text": "Archivo creado con éxito:\n{path}",
        "msg_error_title": "Error",
        "msg_error_zip": "Error crítico al crear el archivo: {err}"
    },
    "de": {
        "app_title": "Microsoft Edge TTS - Generator",
        "text_label": "Text zum Vorlesen:",
        "btn_load": "📂 Aus .txt laden",
        "btn_clear": "🗑 Löschen",
        "settings_frame": " Generierungseinstellungen ",
        "lang_label": "Sprache:",
        "region_label": "Region/Dialekt:",
        "gender_label": "Geschlecht:",
        "gender_all": "Beliebig",
        "gender_male": "Männlich",
        "gender_female": "Weiblich",
        "voice_label": "Stimme:",
        "chars_label": "Zeichen pro Fragment:",
        "parallel_label": "Parallele Pakete:",
        "status_ready": "Bereit",
        "status_loading_voices": "Stimmen werden geladen...",
        "btn_start": "Generieren und als ZIP speichern",
        "msg_warning_title": "Warnung",
        "msg_no_text": "Bitte geben Sie Text zum Vorlesen ein.",
        "msg_save_title": "Archiv speichern unter...",
        "status_calc": "Verbleibend: Berechnung...",
        "status_split": "Text in {total} Fragmente aufgeteilt. Sprachausgabe gestartet...",
        "status_progress": "Fragmente fertig: {done} von {total}...",
        "status_zip": "Audiodateien in ein ZIP-Archiv packen...",
        "status_zip_eta": "Verbleibend: Archivierung...",
        "status_done": "Alles fertig! Archiv erfolgreich gespeichert.",
        "eta_left": "Verbleibend: {mins}:{secs}",
        "msg_success_title": "Erfolg",
        "msg_success_text": "Archiv erfolgreich erstellt:\n{path}",
        "msg_error_title": "Fehler",
        "msg_error_zip": "Kritischer Fehler beim Erstellen des Archivs: {err}"
    },
    "fr": {
        "app_title": "Microsoft Edge TTS - Générateur",
        "text_label": "Texte à synthétiser :",
        "btn_load": "📂 Charger depuis .txt",
        "btn_clear": "🗑 Effacer",
        "settings_frame": " Paramètres de génération ",
        "lang_label": "Langue :",
        "region_label": "Région/Dialecte :",
        "gender_label": "Genre de voix :",
        "gender_all": "Tout",
        "gender_male": "Homme",
        "gender_female": "Femme",
        "voice_label": "Voix :",
        "chars_label": "Caractères par fragment :",
        "parallel_label": "Tâches parallèles :",
        "status_ready": "Prêt à travailler",
        "status_loading_voices": "Chargement des voix...",
        "btn_start": "Générer et enregistrer dans un ZIP",
        "msg_warning_title": "Avertissement",
        "msg_no_text": "Veuillez saisir du texte à synthétiser.",
        "msg_save_title": "Enregistrer l'archive sous...",
        "status_calc": "Temps restant : calcul...",
        "status_split": "Texte divisé en {total} fragments. Début de la synthèse...",
        "status_progress": "Fragments complétés : {done} sur {total}...",
        "status_zip": "Assemblage des fichiers audio dans une archive ZIP...",
        "status_zip_eta": "Temps restant : archivage...",
        "status_done": "Tout est fait ! Archive enregistrée avec succès.",
        "eta_left": "Restant : {mins}:{secs}",
        "msg_success_title": "Succès",
        "msg_success_text": "Archive créée avec succès :\n{path}",
        "msg_error_title": "Erreur",
        "msg_error_zip": "Erreur critique lors de la création de l'archive : {err}"
    },
    "pt": {
        "app_title": "Microsoft Edge TTS - Gerador",
        "text_label": "Texto para narrar:",
        "btn_load": "📂 Carregar de .txt",
        "btn_clear": "🗑 Limpar",
        "settings_frame": " Configurações de Geração ",
        "lang_label": "Idioma:",
        "region_label": "Região/Dialeto:",
        "gender_label": "Gênero da voz:",
        "gender_all": "Qualquer",
        "gender_male": "Masculino",
        "gender_female": "Feminino",
        "voice_label": "Voz:",
        "chars_label": "Caracteres por fragmento:",
        "parallel_label": "Pacotes paralelos:",
        "status_ready": "Pronto para trabalhar",
        "status_loading_voices": "Carregando vozes...",
        "btn_start": "Gerar e salvar em ZIP",
        "msg_warning_title": "Aviso",
        "msg_no_text": "Por favor, insira o texto para narrar.",
        "msg_save_title": "Salvar arquivo como...",
        "status_calc": "Restante: calculando...",
        "status_split": "Texto dividido em {total} fragmentos. Iniciando narração...",
        "status_progress": "Fragmentos concluídos: {done} de {total}...",
        "status_zip": "Agrupando arquivos de áudio em um arquivo ZIP...",
        "status_zip_eta": "Restante: arquivando...",
        "status_done": "Tudo pronto! Arquivo salvo com sucesso.",
        "eta_left": "Restante: {mins}:{secs}",
        "msg_success_title": "Sucesso",
        "msg_success_text": "Arquivo criado com sucesso:\n{path}",
        "msg_error_title": "Erro",
        "msg_error_zip": "Erro crítico ao criar o arquivo ZIP: {err}"
    },
    "zh": {
        "app_title": "Microsoft Edge TTS - 生成器",
        "text_label": "待转换文本:",
        "btn_load": "📂 从 .txt 加载",
        "btn_clear": "🗑 清空",
        "settings_frame": " 生成设置 ",
        "lang_label": "语音语言:",
        "region_label": "地区/方言:",
        "gender_label": "声音性别:",
        "gender_all": "不限",
        "gender_male": "男",
        "gender_female": "女",
        "voice_label": "声音:",
        "chars_label": "单段字符数:",
        "parallel_label": "并发任务数:",
        "status_ready": "就绪",
        "status_loading_voices": "正在加载声音...",
        "btn_start": "生成并保存到 ZIP",
        "msg_warning_title": "提示",
        "msg_no_text": "请输入需要转换的文本。",
        "msg_save_title": "将压缩包保存为...",
        "status_calc": "剩余时间: 正在计算...",
        "status_split": "文本已切分为 {total} 个片段。开始转换...",
        "status_progress": "已完成片段: {done} / {total}...",
        "status_zip": "正在将音频文件打包到 ZIP 压缩包...",
        "status_zip_eta": "剩余时间: 正在压缩...",
        "status_done": "大功告成！压缩包已成功保存。",
        "eta_left": "剩余时间: {mins}:{secs}",
        "msg_success_title": "成功",
        "msg_success_text": "压缩包创建成功:\n{path}",
        "msg_error_title": "错误",
        "msg_error_zip": "创建压缩包时发生严重错误: {err}"
    },
    "ja": {
        "app_title": "Microsoft Edge TTS - ジェネレーター",
        "text_label": "読み上げるテキスト:",
        "btn_load": "📂 .txt から読み込み",
        "btn_clear": "🗑 クリア",
        "settings_frame": " 生成設定 ",
        "lang_label": "音声の言語:",
        "region_label": "地域/方言:",
        "gender_label": "音声の性別:",
        "gender_all": "すべて",
        "gender_male": "男性",
        "gender_female": "女性",
        "voice_label": "音声:",
        "chars_label": "1フラグメントの文字数:",
        "parallel_label": "並列処理数:",
        "status_ready": "準備完了",
        "status_loading_voices": "音声リストを読み込んでいます...",
        "btn_start": "音声生成してZIPに保存",
        "msg_warning_title": "警告",
        "msg_no_text": "読み上げるテキストを入力してください。",
        "msg_save_title": "アーカイブを保存...",
        "status_calc": "残り時間: 計算中...",
        "status_split": "テキストを {total} 個のフラグメントに分割しました。音声生成を開始します...",
        "status_progress": "生成完了: {done} / {total}...",
        "status_zip": "オーディオファイルをZIPアーカイブにまとめています...",
        "status_zip_eta": "残り時間: 圧縮中...",
        "status_done": "すべて完了しました！アーカイブが正常に保存されました。",
        "eta_left": "残り時間: {mins}:{secs}",
        "msg_success_title": "成功",
        "msg_success_text": "アーカイブが正常に作成されました:\n{path}",
        "msg_error_title": "エラー",
        "msg_error_zip": "アーカイブ作成中に致命的なエラーが発生しました: {err}"
    },
    "ar": {
        "app_title": "Microsoft Edge TTS - مولد الصوت",
        "text_label": "النص المراد تحويله:",
        "btn_load": "📂 تحميل من .txt",
        "btn_clear": "🗑 مسح",
        "settings_frame": " إعدادات التوليد ",
        "lang_label": "لغة الصوت:",
        "region_label": "المنطقة/اللهجة:",
        "gender_label": "جنس الصوت:",
        "gender_all": "الكل",
        "gender_male": "ذكر",
        "gender_female": "أنثى",
        "voice_label": "الصوت:",
        "chars_label": "عدد الأحرف في الجزء:",
        "parallel_label": "الحزم الموازية:",
        "status_ready": "جاهز للعمل",
        "status_loading_voices": "جاري تحميل الأصوات...",
        "btn_start": "توليد وحفظ في ملف ZIP",
        "msg_warning_title": "تنبيه",
        "msg_no_text": "يرجى إدخال النص لتحويله إلى صوت.",
        "msg_save_title": "حفظ الأرشيف باسم...",
        "status_calc": "الوقت المتبقي: جاري الحساب...",
        "status_split": "تم تقسيم النص إلى {total} أجزاء. جاري بدء التوليد الصوتي...",
        "status_progress": "الأجزاء المكتملة: {done} من {total}...",
        "status_zip": "جاري تجميع الملفات الصوتية في أرشيف ZIP...",
        "status_zip_eta": "الوقت المتبقي: جاري الأرشفة...",
        "status_done": "اكتمل كل شيء! تم حفظ الأرشيف بنجاح.",
        "eta_left": "المتبقي: {mins}:{secs}",
        "msg_success_title": "نجاح",
        "msg_success_text": "تم إنشاء الأرشيف بنجاح:\n{path}",
        "msg_error_title": "خطأ",
        "msg_error_zip": "خطأ خطير أثناء إنشاء الأرشيف: {err}"
    }
}

class VoiceApp:
    def __init__(self, root):
        self.root = root
        self.ui_lang = 'ru'
        self.locales = INTERNAL_FALLBACK_LOCALES
        self.voice_data = defaultdict(lambda: defaultdict(list))
        
        self.root.title(self.t("app_title"))
        self.root.geometry("850x700")
        self.root.minsize(700, 600)
        
        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')
        except:
            pass
            
        self._build_menu()
        self._build_ui()
        
        self.set_ui_state(tk.DISABLED)
        self.update_status(self.t("status_loading_voices"))
        threading.Thread(target=self._fetch_voices_thread, daemon=True).start()

    def t(self, key, **kwargs):
        text = self.locales.get(self.ui_lang, {}).get(key)
        if text is None:
            text = self.locales.get('en', {}).get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except Exception:
                pass
        return text

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        self.lang_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🌐 Language / Язык", menu=self.lang_menu)
        
        native_menu_names = {
            'ru': 'Русский', 'en': 'English', 'uk': 'Українська', 
            'es': 'Español', 'de': 'Deutsch', 'fr': 'Français', 
            'pt': 'Português', 'zh': '中文', 'ja': '日本語', 'ar': 'العربية'
        }
        
        for lang_code in UI_LANGUAGES:
            label_text = native_menu_names.get(lang_code, lang_code.upper())
            self.lang_menu.add_command(
                label=label_text, 
                command=lambda lang=lang_code: self.switch_ui_language(lang)
            )

    def switch_ui_language(self, lang_code):
        self.ui_lang = lang_code
        self.root.title(self.t("app_title"))
        self.text_label.config(text=self.t("text_label"))
        self.load_btn.config(text=self.t("btn_load"))
        self.clear_btn.config(text=self.t("btn_clear"))
        self.settings_frame.config(text=self.t("settings_frame"))
        
        self.lbl_lang.config(text=self.t("lang_label"))
        self.lbl_region.config(text=self.t("region_label"))
        
        # Обновляем переводы для фильтра пола
        self.lbl_gender.config(text=self.t("gender_label"))
        curr_gender_idx = self.gender_combo.current() if self.gender_combo.current() >= 0 else 0
        self.gender_combo['values'] = [self.t("gender_all"), self.t("gender_male"), self.t("gender_female")]
        self.gender_combo.current(curr_gender_idx)
        
        self.lbl_voice.config(text=self.t("voice_label"))
        self.lbl_chars.config(text=self.t("chars_label"))
        self.lbl_parallel.config(text=self.t("parallel_label"))
        self.start_btn.config(text=self.t("btn_start"))
        self.update_status(self.t("status_ready"))
        
        self._update_lang_combo()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        top_buttons_frame = ttk.Frame(main_frame)
        top_buttons_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.text_label = ttk.Label(top_buttons_frame, text=self.t("text_label"), font=("Segoe UI", 10, "bold"))
        self.text_label.pack(side=tk.LEFT)
        
        self.load_btn = ttk.Button(top_buttons_frame, text=self.t("btn_load"), command=self.load_text_file)
        self.load_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.clear_btn = ttk.Button(top_buttons_frame, text=self.t("btn_clear"), command=self.clear_text)
        self.clear_btn.pack(side=tk.RIGHT)
        
        self.text_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Segoe UI", 10), height=10)
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        self.text_area.bind('<Control-v>', self.paste_text)
        
        self.settings_frame = ttk.LabelFrame(main_frame, text=self.t("settings_frame"), padding="15")
        self.settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 1. Выбор основного языка
        self.lbl_lang = ttk.Label(self.settings_frame, text=self.t("lang_label"))
        self.lbl_lang.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.lang_var = tk.StringVar()
        self.lang_combo = ttk.Combobox(self.settings_frame, textvariable=self.lang_var, state="readonly", width=40)
        self.lang_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.lang_combo.bind("<<ComboboxSelected>>", self.on_language_change)
        
        # 2. Выбор региона
        self.lbl_region = ttk.Label(self.settings_frame, text=self.t("region_label"))
        self.lbl_region.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.region_var = tk.StringVar()
        self.region_combo = ttk.Combobox(self.settings_frame, textvariable=self.region_var, state="readonly", width=40)
        self.region_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.region_combo.bind("<<ComboboxSelected>>", self.update_voice_list)
        
        # 3. ФИЛЬТР ПО ПОЛУ
        self.lbl_gender = ttk.Label(self.settings_frame, text=self.t("gender_label"))
        self.lbl_gender.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.gender_var = tk.StringVar()
        self.gender_combo = ttk.Combobox(self.settings_frame, textvariable=self.gender_var, state="readonly", width=40)
        self.gender_combo['values'] = [self.t("gender_all"), self.t("gender_male"), self.t("gender_female")]
        self.gender_combo.current(0)
        self.gender_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.gender_combo.bind("<<ComboboxSelected>>", self.update_voice_list)
        
        # 4. Выбор чистого голоса
        self.lbl_voice = ttk.Label(self.settings_frame, text=self.t("voice_label"))
        self.lbl_voice.grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.voice_var = tk.StringVar()
        self.voice_combo = ttk.Combobox(self.settings_frame, textvariable=self.voice_var, state="readonly", width=40)
        self.voice_combo.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Технические настройки
        self.lbl_chars = ttk.Label(self.settings_frame, text=self.t("chars_label"))
        self.lbl_chars.grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.char_var = tk.IntVar(value=5000)
        self.char_scale = ttk.Scale(self.settings_frame, from_=500, to=20000, variable=self.char_var, command=self.update_char_label)
        self.char_scale.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        self.char_label = ttk.Label(self.settings_frame, text="5000")
        self.char_label.grid(row=4, column=2, sticky=tk.W, padx=5, pady=5)
        
        self.lbl_parallel = ttk.Label(self.settings_frame, text=self.t("parallel_label"))
        self.lbl_parallel.grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.parallel_var = tk.IntVar(value=10)
        self.parallel_scale = ttk.Scale(self.settings_frame, from_=1, to=20, variable=self.parallel_var, command=self.update_parallel_label)
        self.parallel_scale.grid(row=5, column=1, sticky=tk.EW, padx=5, pady=5)
        self.parallel_label = ttk.Label(self.settings_frame, text="10")
        self.parallel_label.grid(row=5, column=2, sticky=tk.W, padx=5, pady=5)
        
        self.settings_frame.columnconfigure(1, weight=1)
        
        self.status_var = tk.StringVar(value="Ожидание...")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("Segoe UI", 10, "italic"), foreground="gray")
        self.status_label.pack(anchor=tk.W, pady=(0, 5))
        
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.percent_label = ttk.Label(progress_frame, text="0%", font=("Segoe UI", 9, "bold"))
        self.percent_label.pack(side=tk.LEFT, padx=(10, 5))
        
        self.eta_label = ttk.Label(progress_frame, text="--:--", font=("Segoe UI", 9))
        self.eta_label.pack(side=tk.LEFT)
        
        self.start_btn = ttk.Button(main_frame, text=self.t("btn_start"), command=self.start_processing_thread)
        self.start_btn.pack(fill=tk.X, ipady=8)

    def _fetch_voices_thread(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            voices = loop.run_until_complete(edge_tts.list_voices())
            loop.close()
            self.root.after(0, self._process_fetched_voices, voices)
        except Exception as e:
            print(f"Ошибка сети: {e}")
            self.root.after(0, self.update_status, "Сетевая ошибка. Перезапустите приложение.")

    def _process_fetched_voices(self, voices):
        self.voice_data.clear()
        
        for v in voices:
            locale = v['Locale']
            parts = locale.split('-')
            base_lang = parts[0]
            region = parts[1] if len(parts) > 1 else base_lang.upper()
            
            voice_obj = {
                'ShortName': v['ShortName'],
                'Gender': v.get('Gender', 'Unknown')
            }
            self.voice_data[base_lang][region].append(voice_obj)
            
        self._update_lang_combo()
        self.set_ui_state(tk.NORMAL)
        self.update_status(self.t("status_ready"))

    def _update_lang_combo(self):
        if not self.voice_data:
            return
            
        top_list = []
        other_list = []
        
        for base_lang in self.voice_data.keys():
            translated_name = BASE_LANGS.get(base_lang, {}).get(self.ui_lang)
            if not translated_name:
                translated_name = BASE_LANGS.get(base_lang, {}).get('en', base_lang.upper())
                
            display_str = f"{base_lang} | {translated_name}"
            
            # Разделяем языки на Топ-10 интерфейса и все остальные
            if base_lang in UI_LANGUAGES:
                top_list.append((UI_LANGUAGES.index(base_lang), display_str))
            else:
                other_list.append(display_str)
                
        # Сортируем ТОП-10 в порядке следования UI_LANGUAGES, а остальные по алфавиту
        top_list.sort(key=lambda x: x[0])
        top_list = [item[1] for item in top_list]
        other_list.sort(key=lambda x: x.split(' | ')[1])
        
        display_list = top_list + other_list
        
        current_selection = self.lang_combo.get()
        current_code = current_selection.split(' | ')[0] if current_selection else None
        
        self.lang_combo['values'] = display_list
        
        if current_code and any(current_code in item for item in display_list):
            for i, val in enumerate(display_list):
                if val.startswith(f"{current_code} |"):
                    self.lang_combo.current(i)
                    break
        else:
            default_index = 0
            for i, val in enumerate(display_list):
                if val.startswith(f"{self.ui_lang} |"):
                    default_index = i
                    break
            self.lang_combo.current(default_index)
            
        self.on_language_change()

    def on_language_change(self, event=None):
        selected_lang_full = self.lang_combo.get()
        if not selected_lang_full:
            return
            
        base_lang = selected_lang_full.split(' | ')[0]
        regions_dict = self.voice_data.get(base_lang, {})
        
        display_list = []
        for region_code in regions_dict.keys():
            translated_region = REGIONS.get(region_code, {}).get(self.ui_lang)
            if not translated_region:
                translated_region = REGIONS.get(region_code, {}).get('en', region_code)
                
            display_list.append(f"{region_code} | {translated_region}")
            
        display_list.sort(key=lambda x: x.split(' | ')[1])
        self.region_combo['values'] = display_list
        
        default_region_code = DEFAULT_REGIONS.get(base_lang)
        selected_index = 0
        if default_region_code:
            for i, val in enumerate(display_list):
                if val.startswith(f"{default_region_code} |"):
                    selected_index = i
                    break
                    
        if display_list:
            self.region_combo.current(selected_index)
            
        self.update_voice_list()

    def update_voice_list(self, event=None):
        selected_lang_full = self.lang_combo.get()
        selected_region_full = self.region_combo.get()
        
        if not selected_lang_full or not selected_region_full:
            return
            
        base_lang = selected_lang_full.split(' | ')[0]
        region_code = selected_region_full.split(' | ')[0]
        
        voices = self.voice_data.get(base_lang, {}).get(region_code, [])
        
        # Получаем выбранный фильтр пола
        sel_gender_text = self.gender_combo.get()
        filter_gender = 'All'
        if sel_gender_text == self.t("gender_male"):
            filter_gender = 'Male'
        elif sel_gender_text == self.t("gender_female"):
            filter_gender = 'Female'
        
        display_list = []
        for v in voices:
            short_name = v['ShortName']
            gender_en = v['Gender']
            
            # Применяем фильтр по полу
            if filter_gender != 'All' and gender_en != filter_gender:
                continue
            
            # Очищаем имя от префиксов (оставляем только чистое имя голоса)
            clean_name = short_name.replace(f"{base_lang}-{region_code}-", "")
            
            display_list.append(f"{clean_name} | {short_name}")
            
        self.voice_combo['values'] = display_list
        if display_list:
            self.voice_combo.current(0)
        else:
            self.voice_combo.set("") # Очищаем, если голосов с таким полом нет
            
    def paste_text(self, event):
        try:
            text = self.root.clipboard_get()
            self.text_area.insert(tk.INSERT, text)
        except tk.TclError:
            pass
        return 'break'

    def clear_text(self):
        self.text_area.delete('1.0', tk.END)

    def load_text_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not filepath: return
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                self.text_area.delete('1.0', tk.END)
                self.text_area.insert(tk.END, file.read())
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='cp1251') as file:
                self.text_area.delete('1.0', tk.END)
                self.text_area.insert(tk.END, file.read())

    def update_char_label(self, event=None):
        self.char_var.set(int(self.char_scale.get()))
        self.char_label.config(text=str(self.char_var.get()))

    def update_parallel_label(self, event=None):
        self.parallel_var.set(int(self.parallel_scale.get()))
        self.parallel_label.config(text=str(self.parallel_var.get()))

    def set_ui_state(self, state):
        self.start_btn.config(state=state)
        self.load_btn.config(state=state)
        self.clear_btn.config(state=state)
        self.text_area.config(state=state)
        self.char_scale.config(state=state)
        self.parallel_scale.config(state=state)
        self.lang_combo.config(state=state)
        self.region_combo.config(state=state)
        self.gender_combo.config(state=state)
        self.voice_combo.config(state=state)

    def update_status(self, text):
        self.root.after(0, lambda: self.status_var.set(text))

    def update_progress_ui(self, progress_val, percent_text, eta_text):
        self.progress_bar.config(value=progress_val)
        self.percent_label.config(text=percent_text)
        self.eta_label.config(text=eta_text)

    def start_processing_thread(self):
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning(self.t("msg_warning_title"), self.t("msg_no_text"))
            return
            
        if not self.voice_combo.get():
            messagebox.showwarning(self.t("msg_warning_title"), "Пожалуйста, выберите голос. Возможно, для данного пола голоса отсутствуют.")
            return
            
        zip_path = filedialog.asksaveasfilename(title=self.t("msg_save_title"), defaultextension=".zip", filetypes=[("ZIP Archive", "*.zip")])
        if not zip_path: return 
            
        self.set_ui_state(tk.DISABLED)
        self.update_progress_ui(0, "0%", self.t("status_calc"))
        threading.Thread(target=self.run_async_loop, args=(text, zip_path), daemon=True).start()

    def run_async_loop(self, text, zip_path):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.process_text_async(text, zip_path))
            loop.close()
        except Exception as e:
            self.root.after(0, lambda: self.update_status("Ошибка асинхронного цикла."))
            print(f"Loop Error: {e}")

    async def process_text_async(self, text, zip_path):
        selected_voice_full = self.voice_combo.get()
        voice_code = selected_voice_full.split(' | ')[1]
        
        max_chars = self.char_var.get()
        parallel_tasks = self.parallel_var.get()
        
        chunks = [text[i:i + max_chars] for i in range(0, len(text), max_chars)]
        total_chunks = len(chunks)
        
        self.update_status(self.t("status_split", total=total_chunks))
        
        semaphore = asyncio.Semaphore(parallel_tasks)
        generated_files = []
        completed_count = 0
        start_time = time.time()
        
        async def generate_chunk(chunk_text, file_name):
            nonlocal completed_count
            async with semaphore:
                try:
                    communicate = edge_tts.Communicate(chunk_text, voice_code)
                    await communicate.save(file_name)
                    completed_count += 1
                    
                    progress_val = (completed_count / total_chunks) * 90
                    percent_str = f"{int(progress_val)}%"
                    
                    elapsed_time = time.time() - start_time
                    time_per_chunk = elapsed_time / completed_count
                    remaining_chunks = total_chunks - completed_count
                    remaining_time = max(0, time_per_chunk * remaining_chunks)
                    
                    mins, secs = divmod(int(remaining_time), 60)
                    eta_str = self.t("eta_left", mins=f"{mins:02d}", secs=f"{secs:02d}")
                    
                    self.root.after(0, lambda p=progress_val, pct=percent_str, eta=eta_str: self.update_progress_ui(p, pct, eta))
                    self.update_status(self.t("status_progress", done=completed_count, total=total_chunks))
                except Exception as e:
                    print(f"Ошибка на файле {file_name}: {e}")

        tasks = []
        for i, chunk in enumerate(chunks):
            file_name = f"output_chunk_{i+1:04d}.mp3"
            generated_files.append(file_name)
            tasks.append(generate_chunk(chunk, file_name))
            
        await asyncio.gather(*tasks)
        await asyncio.sleep(1)
        
        self.update_status(self.t("status_zip"))
        self.root.after(0, lambda: self.update_progress_ui(95, "95%", self.t("status_zip_eta")))
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in generated_files:
                    if os.path.exists(file):
                        added_to_zip = False
                        try:
                            zipf.write(file, os.path.basename(file))
                            added_to_zip = True
                        except Exception as e:
                            print(f"Ошибка записи: {e}")
                            
                        if added_to_zip:
                            for _ in range(5):
                                try:
                                    os.remove(file)
                                    break
                                except Exception:
                                    time.sleep(0.5)
            
            self.update_status(self.t("status_done"))
            self.root.after(0, lambda: self.update_progress_ui(100, "100%", "OK"))
            self.root.after(0, lambda: messagebox.showinfo(self.t("msg_success_title"), self.t("msg_success_text", path=zip_path)))
        except Exception as e:
            self.update_status(self.t("msg_error_title"))
            self.root.after(0, lambda: self.update_progress_ui(0, "Error", "--:--"))
            self.root.after(0, lambda: messagebox.showerror(self.t("msg_error_title"), self.t("msg_error_zip", err=e)))
        finally:
            self.root.after(0, lambda: self.set_ui_state(tk.NORMAL))

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceApp(root)
    root.mainloop()