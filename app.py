import streamlit as st
import uuid
from handler import add_card, move_card, delete_card, get_all_cards

# 初始化看板
def init_board():
    board_id = st.session_state.get("board_id", str(uuid.uuid4()))
    st.session_state.board_id = board_id
    return board_id

# 主应用
def main():
    st.title("Task Management Board")
    
    # 初始化看板
    board_id = init_board()
    
    # 创建4列
    columns = st.columns(4)
    columns[0].header("Tasks")
    columns[1].header("In Progress")
    columns[2].header("Done")
    columns[3].header("BrainStorm")
    
    # 获取所有卡片
    cards = get_all_cards(board_id)
    
    # 按状态分组卡片
    grouped_cards = {
        "Task": [],
        "In Progress": [],
        "Done": [],
        "BrainStorm": []
    }
    
    for card in cards:
        grouped_cards[card["status"]].append(card)
    
    # 显示卡片并处理拖拽
    for i, status in enumerate(["Task", "In Progress", "Done", "BrainStorm"]):
        with columns[i]:
            for card in grouped_cards[status]:
                # 显示卡片内容
                card_container = st.empty()
                card_container.write(f"**{card['content']}**")
                
                # 删除按钮
                delete_btn = st.button("🗑️", key=f"delete_{card['id']}")
                if delete_btn:
                    if st.confirmation_dialog("Confirm Delete", "Are you sure you want to delete this card?"):
                        delete_card(card["id"])
                        st.rerun()
                
                # 拖拽功能
                new_status = st.selectbox(
                    "Move to",
                    ["Task", "In Progress", "Done", "BrainStorm"],
                    index=["Task", "In Progress", "Done", "BrainStorm"].index(status),
                    key=f"move_{card['id']}",
                    label_visibility="collapsed"
                )
                
                if new_status != status:
                    move_card(card["id"], new_status)
                    st.rerun()
            
            # 添加新卡片
            new_content = st.text_input("Add new card", key=f"add_{status}")
            if st.button("Add", key=f"add_btn_{status}") and new_content:
                add_card(board_id, new_content, status)
                st.rerun()

if __name__ == "__main__":
    main()
