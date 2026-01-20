"""
معالجات المكافآت والتبادل.

يحتوي على معالجات الأزرار والأوامر المتعلقة بالمكافآت والتبادل.
"""

import logging
from typing import Optional
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from src.database import get_user, save_user
from src.models.user import User
from src.utils.reward_manager import reward_manager
from src.utils.exceptions import (
    InsufficientPoints,
    RewardNotFound,
    InvalidOperation,
)

logger: logging.Logger = logging.getLogger(__name__)


async def show_rewards_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    عرض قائمة المكافآت المتاحة للمستخدم.
    
    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق
        
    Returns:
        None
    """
    query = update.callback_query
    user_id: int = query.from_user.id
    
    try:
        db_user: Optional[User] = get_user(user_id)
        
        if not db_user:
            await query.edit_message_text("❌ خطأ: لم يتم العثور على بياناتك")
            return
        
        available_rewards = reward_manager.get_available_rewards(db_user.points)
        
        if not available_rewards:
            text: str = (
                "🏪 **المتجر - المكافآت**\n\n"
                "لا توجد مكافآت متاحة حاليًا بنقاطك الحالية.\n"
                f"نقاطك الحالية: {db_user.points} 🎯"
            )
            keyboard = [[InlineKeyboardButton("🔙 العودة", callback_data="main_menu")]]
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
        
        # بناء قائمة المكافآت
        text = (
            f"🏪 **المتجر - المكافآت المتاحة**\n\n"
            f"نقاطك الحالية: **{db_user.points}** 🎯\n\n"
        )
        
        keyboard = []
        for reward in available_rewards[:5]:  # الحد الأقصى 5 مكافآت لتجنب الازدحام
            text += (
                f"**{reward.name}**\n"
                f"{reward.description}\n"
                f"التكلفة: {reward.cost} نقطة\n"
                f"النوع: {reward.reward_type.value}\n\n"
            )
            
            button_text = f"🎁 {reward.name} ({reward.cost})"
            keyboard.append(
                [InlineKeyboardButton(button_text, callback_data=f"claim_reward_{reward.reward_id}")]
            )
        
        keyboard.append([InlineKeyboardButton("🔙 العودة", callback_data="main_menu")])
        
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        logger.debug(f"عرض المكافآت للمستخدم {user_id}")
        
    except Exception as e:
        await query.edit_message_text(f"❌ خطأ: {str(e)}")
        logger.error(f"خطأ في عرض المكافآت: {str(e)}", exc_info=True)


async def claim_reward_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    reward_id: int
) -> None:
    """
    معالج الحصول على مكافأة.
    
    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق
        reward_id (int): معرّف المكافأة
        
    Returns:
        None
    """
    query = update.callback_query
    user_id: int = query.from_user.id
    
    try:
        db_user: Optional[User] = get_user(user_id)
        
        if not db_user:
            await query.answer("❌ خطأ: لم يتم العثور على بياناتك", show_alert=True)
            return
        
        # محاولة الحصول على المكافأة
        success, message = reward_manager.claim_reward(db_user, reward_id)
        
        if success:
            # حفظ البيانات المحدثة
            save_user(db_user)
            
            await query.answer("✅ تم الحصول على المكافأة!", show_alert=True)
            
            # إرسال رسالة تأكيد
            confirmation_text: str = (
                f"✅ **تم الحصول على المكافأة!**\n\n"
                f"{message}\n"
                f"نقاطك المتبقية: {db_user.points}"
            )
            
            await query.edit_message_text(confirmation_text, parse_mode="Markdown")
            logger.info(f"المستخدم {user_id} حصل على مكافأة برقم {reward_id}")
            
    except InsufficientPoints as e:
        await query.answer(f"⚠️ {e.message}", show_alert=True)
    except RewardNotFound as e:
        await query.answer(f"❌ {e.message}", show_alert=True)
    except InvalidOperation as e:
        await query.answer(f"⚠️ {e.message}", show_alert=True)
    except Exception as e:
        await query.answer("❌ حدث خطأ غير متوقع", show_alert=True)
        logger.error(f"خطأ في الحصول على المكافأة: {str(e)}", exc_info=True)


async def show_store_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    عرض قائمة المتجر الرئيسية.
    
    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق
        
    Returns:
        None
    """
    query = update.callback_query
    
    text: str = (
        "🏪 **المتجر**\n\n"
        "اختر ما تريد:\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("🎁 المكافآت", callback_data="store_rewards")],
        [InlineKeyboardButton("⚡ الميزات الخاصة", callback_data="store_features")],
        [InlineKeyboardButton("🔙 العودة", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    logger.debug(f"عرض قائمة المتجر للمستخدم {query.from_user.id}")


async def admin_manage_rewards(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    عرض قائمة إدارة المكافآت للمسؤول.
    
    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق
        
    Returns:
        None
    """
    query = update.callback_query
    
    rewards = reward_manager.get_all_rewards()
    
    text: str = (
        "🎁 **إدارة المكافآت**\n\n"
        f"إجمالي المكافآت: {len(rewards)}\n\n"
    )
    
    for reward in rewards[:5]:
        status = "✅ مفعلة" if reward.is_active else "❌ معطلة"
        text += (
            f"**{reward.name}** {status}\n"
            f"التكلفة: {reward.cost} نقطة\n"
            f"الاستخدامات: {reward.claim_count}"
            f"{f'/{reward.max_claims}' if reward.max_claims else ''}\n\n"
        )
    
    keyboard = [
        [InlineKeyboardButton("➕ إضافة مكافأة", callback_data="admin_add_reward")],
        [InlineKeyboardButton("✏️ تعديل", callback_data="admin_edit_reward")],
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_reward_stats")],
        [InlineKeyboardButton("🔙 الرجوع", callback_data="admin_panel")]
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    logger.debug(f"عرض إدارة المكافآت للمسؤول {query.from_user.id}")