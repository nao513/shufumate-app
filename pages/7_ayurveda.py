def get_current_state_advice(
    sweet_craving,
    salty_craving,
    fatigue,
    irritable,
    sleepy_after_meal,
    swelling,
    coldness,
    constipation_now,
    dry_skin
):
    messages = []

    if sweet_craving:
        messages.append("甘いものが欲しい時は、疲れやストレスがたまっていることがあります。まずは食事の抜けや睡眠不足がないか見直してみましょう。")
    if salty_craving:
        messages.append("しょっぱいものが欲しい時は、疲れや水分バランスの乱れが出ていることがあります。汁物や温かい食事で整えるのもおすすめです。")
    if fatigue:
        messages.append("だるさや疲れが続く時は、食事・睡眠・冷えの影響が重なっていることがあります。無理を減らして整える時間をとりましょう。")
    if irritable:
        messages.append("イライラしやすい時は、がんばりすぎや空腹、睡眠不足の影響が出ていることがあります。")
    if sleepy_after_meal:
        messages.append("食後すぐ眠くなる時は、食べ方や量、血糖の乱れが関係していることがあります。食べすぎや急いで食べる習慣を見直してみましょう。")
    if swelling:
        messages.append("むくみやすい時は、水分代謝の低下や冷え、塩分のとりすぎが関係していることがあります。")
    if coldness:
        messages.append("冷えやすい時は、体を温める食事や湯船、軽い運動を意識すると整いやすくなります。")
    if constipation_now:
        messages.append("便秘ぎみの時は、水分、温かい食事、リズムある生活を意識してみてください。")
    if dry_skin:
        messages.append("乾燥しやすい時は、体の内側の乾きや冷えも関係していることがあります。温かい汁物や油分を少し意識するとよいです。")

    if not messages:
        return "大きな乱れは目立たなそうです。今の生活リズムをベースに、無理なく整えていきましょう。"

    return "\n\n".join(messages)
