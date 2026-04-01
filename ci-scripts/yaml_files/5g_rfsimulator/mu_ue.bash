#!/bin/bash

# ==========================================
# OAI 5G 本地開發智能啟動腳本 (增強版)
# 包含完整的依賴檢測與 Volume 驗證
# ==========================================

# 顏色定義 (增強可讀性)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ==========================================
# 使用方法
# ==========================================
if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: Please specify number of UEs${NC}"
    echo "Usage: $0 <number_of_ues>"
    echo "Example: $0 10"
    exit 1
fi

NUM_UES=$1

# 驗證是否為正整數
if ! [[ "$NUM_UES" =~ ^[0-9]+$ ]] || [ "$NUM_UES" -le 0 ] || [ "$NUM_UES" -gt 28 ]; then
    echo -e "${RED}❌ Error: Number of UEs must be between 1 and 28${NC}"
    exit 1
fi

echo "================================================"
echo "🚀 Starting OAI 5G with $NUM_UES UEs (Local Mode)"
echo "================================================"

# ==========================================
# 環境變數設定
# ==========================================
export GNB_IMG=gnb-local
export NRUE_IMG=ue-local
export REGISTRY=""
export TAG=latest

CMD="docker compose -f docker-compose.yaml -f local-override.yaml"

echo -e "${GREEN}📦 Using Local Images: $GNB_IMG / $NRUE_IMG${NC}"

# ==========================================
# 前置檢查 1: 驗證本地編譯產物是否存在
# ==========================================
echo ""
echo "🔍 Step 0: Validating local build artifacts..."

# 計算相對路徑 (假設腳本在 ci-scripts/yaml_files/5g_rfsimulator/)
BASE_PATH="../../../cmake_targets/ran_build/build"
REQUIRED_FILES=(
    "$BASE_PATH/nr-softmodem"
    "$BASE_PATH/nr-uesoftmodem"
    "$BASE_PATH/librfsimulator.so"
)

MISSING_FILES=false
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}   ✗ Missing: $file${NC}"
        MISSING_FILES=true
    else
        echo -e "${GREEN}   ✓ Found: $file${NC}"
    fi
done

if [ "$MISSING_FILES" = true ]; then
    echo -e "${RED}❌ Critical Error: Required binaries are missing!${NC}"
    echo "Please compile OAI first:"
    echo "  cd ~/openairinterface5g/cmake_targets/ran_build/build"
    echo "  ninja nr-softmodem nr-uesoftmodem"
    exit 1
fi

# 檢查 crashdumps 目錄
CRASHDUMP_DIR="../../../crashdumps"
if [ ! -d "$CRASHDUMP_DIR" ]; then
    echo -e "${YELLOW}   ⚠️  Crashdump directory not found, creating...${NC}"
    mkdir -p "$CRASHDUMP_DIR"
    echo -e "${GREEN}   ✓ Created: $CRASHDUMP_DIR${NC}"
else
    echo -e "${GREEN}   ✓ Crashdump directory exists${NC}"
fi

# ==========================================
# 前置檢查 2: 驗證 Docker Compose 配置
# ==========================================
echo ""
echo "🔍 Validating Docker Compose configuration..."

if ! $CMD config > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker Compose configuration is invalid!${NC}"
    echo "Run this to see details:"
    echo "  $CMD config"
    exit 1
else
    echo -e "${GREEN}✓ Docker Compose configuration is valid${NC}"
fi

# ==========================================
# Step 1: 智能啟動核心網與 gNB
# ==========================================
echo ""
echo "🔍 Step 1: Checking Core Network status..."

CORE_SERVICES="mysql oai-amf oai-smf oai-upf oai-ext-dn"
NEED_START_CORE=false

for service in $CORE_SERVICES; do
    if ! docker ps --format '{{.Names}}' | grep -q "rfsim5g-${service}"; then
        echo -e "${YELLOW}   ⚠️  ${service} is not running${NC}"
        NEED_START_CORE=true
    else
        echo -e "${GREEN}   ✅ ${service} is already running${NC}"
    fi
done

if [ "$NEED_START_CORE" = true ]; then
    echo "🔄 Starting Core Network components..."
    $CMD up -d $CORE_SERVICES
    echo "⏳ Waiting 15 seconds for Core Network to stabilize..."
    sleep 15
else
    echo -e "${GREEN}✅ All Core Network services are already running${NC}"
fi

# ==========================================
# Step 2: 檢查並啟動 rebuild-nr-softmodems 服務
# ==========================================
echo ""
echo "🔍 Step 2: Checking rebuild-nr-softmodems service..."

# 檢查這個服務是否曾經成功執行
if docker ps -a --format '{{.Names}}\t{{.State}}' | grep "rebuild-nr-softmodems" | grep -q "exited"; then
    REBUILD_STATUS=$(docker ps -a --format '{{.Names}}\t{{.State}}\t{{.Status}}' | grep "rebuild-nr-softmodems")
    if echo "$REBUILD_STATUS" | grep -q "Exited (0)"; then
        echo -e "${GREEN}✅ rebuild-nr-softmodems already completed successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  rebuild-nr-softmodems failed previously, restarting...${NC}"
        docker rm -f $(docker ps -a --filter "name=rebuild-nr-softmodems" -q) 2>/dev/null
        $CMD up -d rebuild-nr-softmodems
        echo "⏳ Waiting for rebuild to complete..."
        sleep 10
    fi
else
    echo "🔄 Starting rebuild-nr-softmodems service..."
    $CMD up -d rebuild-nr-softmodems
    echo "⏳ Waiting for rebuild to complete..."
    sleep 10
fi

# ==========================================
# Step 3: 啟動 gNB
# ==========================================
echo ""
echo "🔍 Step 3: Checking gNB status..."

if ! docker ps --format '{{.Names}}' | grep -q "rfsim5g-oai-gnb"; then
    echo "🔄 Starting gNB..."
    $CMD up -d oai-gnb
    echo "⏳ Waiting 20 seconds for gNB to be fully ready..."
    sleep 20
else
    echo -e "${GREEN}✅ gNB is already running${NC}"
fi

# 健康檢查
if docker ps | grep rfsim5g-oai-gnb | grep -q "healthy"; then
    echo -e "${GREEN}✅ gNB is healthy!${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: gNB might not be fully ready yet. Continuing anyway...${NC}"
fi

# ==========================================
# 前置檢查 3: 驗證 Volume 掛載
# ==========================================
echo ""
echo "🔍 Verifying Volume mounts for gNB..."

GNB_MOUNTS=$(docker inspect rfsim5g-oai-gnb --format '{{ json .Mounts }}' 2>/dev/null)
if echo "$GNB_MOUNTS" | grep -q "nr-softmodem"; then
    echo -e "${GREEN}✓ nr-softmodem is correctly mounted${NC}"
else
    echo -e "${RED}✗ Warning: nr-softmodem mount not detected${NC}"
fi

if echo "$GNB_MOUNTS" | grep -q "librfsimulator.so"; then
    echo -e "${GREEN}✓ librfsimulator.so is correctly mounted${NC}"
else
    echo -e "${RED}✗ Warning: librfsimulator.so mount not detected${NC}"
fi

# ==========================================
# Step 4: 動態計算 UE 分批策略
# ==========================================
echo ""
echo "📊 Step 4: Calculating UE batch strategy..."

BATCH1=$(( (NUM_UES + 1) / 2 ))
BATCH2=$(( NUM_UES - BATCH1 ))

echo "   Total UEs: $NUM_UES"
echo "   Batch 1: UE 1 ~ $BATCH1 ($BATCH1 UEs)"
if [ $BATCH2 -gt 0 ]; then
    BATCH2_START=$(( BATCH1 + 1 ))
    echo "   Batch 2: UE $BATCH2_START ~ $NUM_UES ($BATCH2 UEs)"
fi

# ==========================================
# Step 5: 啟動第一批 UE
# ==========================================
echo ""
echo "🚀 Step 5: Starting Batch 1 (UE 1-$BATCH1)..."

UE_LIST_BATCH1=$(seq -f "oai-nr-ue%.0f" 1 $BATCH1)
$CMD up -d $UE_LIST_BATCH1

echo -e "${GREEN}✅ Batch 1 started${NC}"
echo "⏳ Waiting 10 seconds before next batch..."
sleep 10

# ==========================================
# Step 6: 啟動第二批 UE
# ==========================================
if [ $BATCH2 -gt 0 ]; then
    echo ""
    echo "🚀 Step 6: Starting Batch 2 (UE $BATCH2_START-$NUM_UES)..."
    
    BATCH2_START=$(( BATCH1 + 1 ))
    UE_LIST_BATCH2=$(seq -f "oai-nr-ue%.0f" $BATCH2_START $NUM_UES)
    $CMD up -d $UE_LIST_BATCH2
    
    echo -e "${GREEN}✅ Batch 2 started${NC}"
fi

# ==========================================
# 最終驗證
# ==========================================
echo ""
echo "🔍 Final Verification: Checking UE health status..."
sleep 5

HEALTHY_COUNT=0
TOTAL_EXPECTED=$NUM_UES

for i in $(seq 1 $NUM_UES); do
    if docker ps --format '{{.Names}}\t{{.Status}}' | grep "rfsim5g-oai-nr-ue${i}" | grep -q "healthy"; then
        HEALTHY_COUNT=$((HEALTHY_COUNT + 1))
    fi
done

echo "   Healthy UEs: $HEALTHY_COUNT / $TOTAL_EXPECTED"

if [ $HEALTHY_COUNT -eq $TOTAL_EXPECTED ]; then
    echo -e "${GREEN}✅ All UEs are healthy!${NC}"
elif [ $HEALTHY_COUNT -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Some UEs are still starting...${NC}"
else
    echo -e "${RED}❌ Warning: No UEs are healthy yet. Check logs.${NC}"
fi

# ==========================================
# 完成提示
# ==========================================
echo ""
echo "================================================"
echo -e "${GREEN}✅ All $NUM_UES UEs started using LOCAL images!${NC}"
echo "================================================"
echo ""
echo "📋 Quick Commands:"
echo "   Check all containers:"
echo "     $CMD ps"
echo ""
echo "   Check UE status:"
echo "     $CMD ps | grep oai-nr-ue"
echo ""
echo "   Check AMF logs (for registration):"
echo "     docker logs rfsim5g-oai-amf -f"
echo ""
echo "   Check specific UE logs:"
echo "     docker logs rfsim5g-oai-nr-ue1 -f"
echo ""
echo "   Stop all:"
echo "     $CMD down"
echo "================================================"

# ./mu_ue 8 
#open 8 ue