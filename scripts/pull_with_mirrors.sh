#!/bin/bash

echo "=== 智能镜像拉取 ==="

# 实用的镜像源列表（按成功率排序）
mirrors=(
    "docker.m.daocloud.io"
    "dockerhub.azk8s.cn"
    "registry.docker-cn.com"
    "docker.io"
)

images=(
    "postgres:15-alpine"
    "redis:7-alpine"
)

# 智能拉取函数
pull_image() {
    local image=$1
    local success=false
    
    for mirror in "${mirrors[@]}"; do
        echo "尝试从 $mirror 拉取 $image"
        
        if [[ "$mirror" == "docker.io" ]]; then
            pull_cmd="docker pull $image"
        else
            pull_cmd="docker pull $mirror/$image"
        fi
        
        if timeout 60 $pull_cmd; then
            # 重新标记为标准名称
            if [[ "$mirror" != "docker.io" ]]; then
                docker tag "$mirror/$image" "$image"
            fi
            echo "✓ 成功拉取: $image"
            success=true
            break
        else
            echo "✗ 失败: $mirror/$image"
        fi
    done
    
    if [[ "$success" != "true" ]]; then
        echo "⚠ 无法拉取: $image"
        return 1
    fi
}

# 拉取所有镜像
for image in "${images[@]}"; do
    pull_image "$image"
done

echo "=== 镜像拉取完成 ==="
docker images | grep -E "(postgres|redis)"