EXAMPLE_STEPS_LIST = [
    {
        "model_output": {
            "thinking": "Starting by navigating to the target homepage to begin verification process.",
            "action": [{"go_to_url": {"url": "https://debugg.ai"}}],
        },
        "result": [
            {
                "is_done": False,
                "success": True,
                "error": None,
                "long_term_memory": "Successfully navigated to homepage and found Sandbox header text visible.",
            }
        ],
        "state": {
            "url": "https://debugg.ai",
            "title": "Debugg AI - AI-Powered Testing Platform",
            "interacted_element": [],
        },
        "metadata": {
            "step_start_time": 1753997156.1953292,
            "step_end_time": 1753997203.220958,
            "step_number": 1,
        },
    },
    {
        "model_output": {
            "thinking": "Now I need to locate and click on the main navigation or header element.",
            "action": [{"click_element": {"index": 0}}],
        },
        "result": [
            {
                "is_done": False,
                "success": True,
                "error": None,
                "long_term_memory": "Clicked on header element to explore the page structure.",
            }
        ],
        "state": {
            "url": "https://debugg.ai",
            "title": "Debugg AI - AI-Powered Testing Platform",
            "interacted_element": [
                {
                    "xpath": "//header//h1",
                    "css_selector": "header h1",
                    "text_content": "Debugg AI",
                    "attributes": {"class": "text-2xl font-bold text-gray-900"},
                }
            ],
        },
        "metadata": {
            "step_start_time": 1753997350.8411188,
            "step_end_time": 1753997369.5740314,
            "step_number": 2,
        },
    },
    {
        "model_output": {
            "thinking": "Let me wait a moment for any dynamic content to load completely.",
            "action": [{"wait": {"seconds": 2}}],
        },
        "result": [
            {
                "is_done": False,
                "success": True,
                "error": None,
                "long_term_memory": "Waited for page to fully load before proceeding.",
            }
        ],
        "state": {
            "url": "https://debugg.ai",
            "title": "Debugg AI - AI-Powered Testing Platform",
            "interacted_element": [],
        },
        "metadata": {
            "step_start_time": 1753997372.2532299,
            "step_end_time": 1753997391.3151274,
            "step_number": 3,
        },
    },
    {
        "model_output": {
            "thinking": "Let me scroll down to explore more content on the page.",
            "action": [{"scroll": {"direction": "down", "amount": 500}}],
        },
        "result": [
            {
                "is_done": False,
                "success": True,
                "error": None,
                "long_term_memory": "Scrolled down the page to view additional content.",
            }
        ],
        "state": {
            "url": "https://debugg.ai",
            "title": "Debugg AI - AI-Powered Testing Platform",
            "interacted_element": [],
        },
        "metadata": {
            "step_start_time": 1753997394.1183739,
            "step_end_time": 1753997414.787713,
            "step_number": 4,
        },
    },
    {
        "model_output": {
            "thinking": "Task completed successfully. I have explored the website structure and interactions.",
            "action": [{"done": {}}],
        },
        "result": [
            {
                "is_done": True,
                "success": True,
                "error": None,
                "long_term_memory": "Successfully completed website exploration and interaction testing.",
            }
        ],
        "state": {
            "url": "https://debugg.ai",
            "title": "Debugg AI - AI-Powered Testing Platform",
            "interacted_element": [],
        },
        "metadata": {
            "step_start_time": 1753997419.0800045,
            "step_end_time": 1753997442.0409794,
            "step_number": 5,
        },
    },
]
