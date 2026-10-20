import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# States
START_MENU, QUESTION_1, QUESTION_2, QUESTION_3 = range(4)

# Dynamic Quiz Questions & Scoring
QUESTIONS = [
    {
        "text": "📊 **Question 1/3:** What is your primary digital goal?",
        "options": [
            ("Increase Brand Awareness", 10),
            ("Generate Leads & Sales", 20),
            ("Automate Operations", 30),
        ],
    },
    {
        "text": "⏱ **Question 2/3:** How much time do you spend weekly on manual tasks?",
        "options": [
            ("Under 5 hours", 10),
            ("5–15 hours", 20),
            ("Over 15 hours", 30),
        ],
    },
    {
        "text": "🚀 **Question 3/3:** What is your current team capacity?",
        "options": [
            ("Solo / Founder", 10),
            ("Small Team (2–10)", 20),
            ("Established Business (10+)", 30),
        ],
    },
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send welcome message and main menu compliant with Telegram Ads."""
    context.user_data["score"] = 0
    keyboard = [
        [InlineKeyboardButton("🎯 Take Business Assessment", callback_data="start_quiz")],
        [InlineKeyboardButton("ℹ️ About This Tool", callback_data="about")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "👋 **Welcome to the Digital Efficiency Diagnostic Tool!**\n\n"
        "This interactive tool evaluates your business workflows and provides "
        "tailored recommendations in under 1 minute.\n\n"
        "Select an option below to begin."
    )

    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

    return START_MENU


async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show informative about screen directly in-bot."""
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="back_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    about_text = (
        "ℹ️ **About SB24 Diagnostics**\n\n"
        "This bot provides automated operational scoring and recommendations "
        "for businesses looking to optimize digital operations.\n\n"
        "• 100% Free & Interactive\n"
        "• Dynamic insights delivered instantly"
    )
    await query.edit_message_text(about_text, reply_markup=reply_markup, parse_mode="Markdown")
    return START_MENU


async def ask_question(query, question_idx, current_score):
    """Helper to ask a quiz question."""
    q_data = QUESTIONS[question_idx]
    keyboard = []
    for text, score_val in q_data["options"]:
        keyboard.append([InlineKeyboardButton(text, callback_data=f"q_{question_idx}_{score_val}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(q_data["text"], reply_markup=reply_markup, parse_mode="Markdown")


async def handle_start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Begin the evaluation."""
    query = update.callback_query
    await query.answer()
    context.user_data["score"] = 0
    await ask_question(query, 0, 0)
    return QUESTION_1


async def handle_q1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process Question 1 and move to Question 2."""
    query = update.callback_query
    await query.answer()
    score_val = int(query.data.split("_")[2])
    context.user_data["score"] += score_val

    await ask_question(query, 1, context.user_data["score"])
    return QUESTION_2


async def handle_q2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process Question 2 and move to Question 3."""
    query = update.callback_query
    await query.answer()
    score_val = int(query.data.split("_")[2])
    context.user_data["score"] += score_val

    await ask_question(query, 2, context.user_data["score"])
    return QUESTION_3


async def handle_q3_and_deliver_results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Calculate dynamic results and present them cleanly."""
    query = update.callback_query
    await query.answer()
    score_val = int(query.data.split("_")[2])
    total_score = context.user_data.get("score", 0) + score_val

    # Dynamic dynamic outcome calculation based on answers
    if total_score <= 40:
        tier = "🌱 **Phase 1: Foundation Building**"
        recommendation = (
            "Your main focus should be setting up simple automated customer response pipelines "
            "and basic content templates to save up to 5 hours weekly."
        )
    elif total_score <= 70:
        tier = "⚡ **Phase 2: Growth Acceleration**"
        recommendation = (
            "You are positioned for digital scaling. Implementing structured CRM tools "
            "and automated bot follow-ups will help capture higher quality leads."
        )
    else:
        tier = "🚀 **Phase 3: High Efficiency Scale**"
        recommendation = (
            "Your workflow demands custom API integrations, deep analytical tracking, "
            "and fully automated support desks to handle high transaction volumes."
        )

    result_text = (
        f"📋 **Your Diagnostic Report**\n\n"
        f"**Efficiency Level:** {tier}\n"
        f"**Score:** {total_score}/90\n\n"
        f"💡 **Key Recommendation:**\n{recommendation}\n\n"
        "---"
    )

    keyboard = [
        [InlineKeyboardButton("🔄 Retake Diagnostic", callback_data="start_quiz")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="back_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(result_text, reply_markup=reply_markup, parse_mode="Markdown")
    return START_MENU


def main() -> None:
    """Run the bot."""
    TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"

    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_MENU: [
                CallbackQueryHandler(handle_start_quiz, pattern="^start_quiz$"),
                CallbackQueryHandler(show_about, pattern="^about$"),
                CallbackQueryHandler(start, pattern="^back_main$"),
            ],
            QUESTION_1: [CallbackQueryHandler(handle_q1, pattern="^q_0_")],
            QUESTION_2: [CallbackQueryHandler(handle_q2, pattern="^q_1_")],
            QUESTION_3: [CallbackQueryHandler(handle_q3_and_deliver_results, pattern="^q_2_")],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
