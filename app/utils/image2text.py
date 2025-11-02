from openai import OpenAI

from core.config import settings


__client = OpenAI(api_key=settings.app.openai_api_key)
__solve_prompt = (
    "Ты — универсальный помощник, решающий задачи в стиле Copilot.\n"
    "\n"
    "Общие правила:\n"
    "1. Если задача математическая:\n"
    "   - Начинай с краткого анализа: область определения, свойства, шаги.\n"
    "   - Дальше решай с помощью Python-кода (с sympy/numpy/matplotlib и т.д. при необходимости).\n"
    "   - Используй школьные/тестовые упрощения (например, ln((x+3)^4) трактуй как 4*ln(x+3) при x>-3).\n"
    "   - Итоговое значение проверяй в коде.\n"
    "\n"
    "2. Если задача программная:\n"
    "   - Напиши рабочий Python-код.\n"
    "   - Покажи пример запуска/вывода.\n"
    "\n"
    "3. Если задача текстовая (логическая, гуманитарная):\n"
    "   - Реши кратко и по существу.\n"
    "   - Если можно, подтверди результат через простой Python-код (например, для подсчётов).\n"
    "\n"
    "Формат ответа всегда один: только ответ и никаких разяснений\n"
    "на выход только вариант или ответ"
)
__model = "gpt-5-mini"


def __call_openai(**payload):
    return __client.responses.create(**payload).output_text.strip()

def solve_task(image_base64: str):
    payload = {
        "model": __model,
        "instructions": __solve_prompt,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Пользователь передал изображение"},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_base64}",
                    },
                ],
            }
        ],
        "tools": [{"type": "code_interpreter", "container": {"type": "auto"}}],
        "tool_choice": "auto",
    }

    return __call_openai(**payload)




