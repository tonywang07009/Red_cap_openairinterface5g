#!/bin/bash
# 檔名: generate_uicc.sh
# 用途: 根據 nrue2.uicc.yaml 生成多個 nrueX.uicc.yaml
# 功能: 自動遞增 IMSI 並且自動遞增 uicc 編號 (nrue3 -> uicc2)

# 設定工作目錄為腳本所在目錄
cd "$(dirname "$0")"



# 顯示使用方式
usage() {
    echo "用法: $0 <動作> <數量>"
    echo "動作:"
    echo "  add    - 新增 UE 設定檔"
    echo "  delete - 刪除 UE 設定檔"
    echo ""
    echo "範例:"
    echo "  $0 add 5       # 新增 5 個 UE (nrue3, nrue4, ...)"
    echo "  $0 delete 3    # 刪除最後 3 個 UE"
    exit 1
}

# 檢查參數
if [ $# -ne 2 ]; then
    usage
fi

ACTION=$1
COUNT=$2

# 檢查數量是否為正整數
if ! [[ "$COUNT" =~ ^[0-9]+$ ]] || [ "$COUNT" -le 0 ]; then
    echo "錯誤: 數量必須是正整數"
    exit 1
fi

# 檢查模板檔案是否存在
TEMPLATE="nrue2.uicc.yaml"
if [ ! -f "$TEMPLATE" ]; then
    echo "錯誤: 找不到模板檔案 $TEMPLATE"
    exit 1
fi

# 找出目前最大的 nrueX 編號
find_max_ue_number() {
    local max=2
    for file in nrue*.uicc.yaml; do
        if [ -f "$file" ]; then
            num=$(echo "$file" | sed 's/nrue\([0-9]*\)\.uicc\.yaml/\1/')
            if [[ "$num" =~ ^[0-9]+$ ]] && [ "$num" -gt "$max" ]; then
                max=$num
            fi
        fi
    done
    echo $max
}

# 新增 UE 設定檔
add_ue() {
    local start_num=$(($(find_max_ue_number) + 1))
    local end_num=$((start_num + COUNT - 1))
    
    echo "開始新增 UE 設定檔..."
    
    for i in $(seq $start_num $end_num); do
        local new_file="nrue${i}.uicc.yaml"
        
        # 複製模板檔案
        cp "$TEMPLATE" "$new_file"
        
        # 計算新的 IMSI 後綴 (從 nrue2 的 002 開始)
        local new_imsi_suffix=$(printf "%03d" $i)
        
        # 計算新的 uicc 編號 (nrue 編號 - 1)
        # 例如: nrue3 -> uicc2, nrue4 -> uicc3
        local uicc_num=$((i - 1))
        
        # 1. 替換 IMSI 的最後三位數字 (假設模板中是 001010000000002)
        sed -i "s/imsi: 001010000000002/imsi: 00101000000${new_imsi_suffix}/" "$new_file"
        
        # 2. 替換 uicc 編號 (假設模板第一行是 uicc1:)
        # 使用 ^uicc1: 來確保只替換行首的那個標籤
        sed -i "s/^uicc1:/uicc${uicc_num}:/" "$new_file"
        
        echo "✓ 已建立 $new_file (uicc${uicc_num}, IMSI: ...${new_imsi_suffix})"
    done
    
    echo ""
    echo "完成！已新增 $COUNT 個 UE 設定檔 (nrue${start_num} 到 nrue${end_num})"
}

# 刪除 UE 設定檔
delete_ue() {
    local max_num=$(find_max_ue_number)
    
    if [ "$max_num" -le 2 ]; then
        echo "錯誤: 沒有可刪除的 UE 設定檔 (只剩 nrue2)"
        exit 1
    fi
    
    local start_num=$((max_num - COUNT + 1))
    
    if [ "$start_num" -le 2 ]; then
        echo "錯誤: 無法刪除，會影響到 nrue2 (模板檔案)"
        echo "目前最大編號: nrue${max_num}，最多可刪除 $((max_num - 2)) 個"
        exit 1
    fi
    
    echo "準備刪除 UE 設定檔..."
    
    for i in $(seq $start_num $max_num); do
        local file="nrue${i}.uicc.yaml"
        if [ -f "$file" ]; then
            rm "$file"
            echo "✓ 已刪除 $file"
        fi
    done
    
    echo ""
    echo "完成！已刪除 $COUNT 個 UE 設定檔"
}

# 執行對應動作
case "$ACTION" in
    add)
        add_ue
        ;;
    delete)
        delete_ue
        ;;
    *)
        echo "錯誤: 未知的動作 '$ACTION'"
        usage
        ;;
esac
