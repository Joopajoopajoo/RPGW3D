        start_a = self.player_angle - FOV / 2
        transparent_tiles = (TileType.TREE.value, TileType.DEAD_TREE.value, TileType.BUSH.value, TileType.ROCK.value, TileType.STANDING_TORCH.value, TileType.ITEM_UNLIT_TORCH.value)
        
        for ray in range(NUM_RAYS):
            angle = start_a + ray * DELTA_ANGLE
            sin_a, cos_a = math.sin(angle), math.cos(angle)
            for d in range(1, MAX_DEPTH, 1):  # FIXED: Changed step from 3 to 1 for proper wall detection
                tx, ty = self.player_x + d * cos_a, self.player_y + d * sin_a
                gx, gy = int(tx/TILE_SIZE), int(ty/TILE_SIZE)
                if 0 <= gx < w and 0 <= gy < h:
                    tile_val = self.map[gy][gx]
                    if tile_val >= 1 and tile_val not in transparent_tiles:
                        dist = d * math.cos(self.player_angle - angle)
                        self.depth_buffer[ray] = dist
                        wh = max(1, int(WALL_HEIGHT_MULTIPLIER / (dist + PARTICLE_EPSILON)))
                        hit_x_offset, hit_y_offset = tx - (gx * TILE_SIZE + TILE_SIZE/2), ty - (gy * TILE_SIZE + TILE_SIZE/2)
                        if abs(hit_x_offset) > abs(hit_y_offset):
                            normal_x, normal_y, off = (1 if hit_x_offset > 0 else -1), 0, ty % TILE_SIZE
                        else:
                            normal_x, normal_y, off = 0, (1 if hit_y_offset > 0 else -1), tx % TILE_SIZE
                        sun_dot = normal_x * sun_vec_x + normal_y * sun_vec_y
                        added_sunlight = max(0, sun_dot) * sun_intensity
                        torch_light = self.lightmap[gy][gx] * self.global_flicker 
                        dist_shade = max(0, min(1.0, 1.0 - (dist / (MAX_DEPTH*0.8))))
                        
                        p_light = max(0, player_light_intensity - (dist * 0.8)) if player_light_intensity > 0 else 0
                        
                        proj_light = 0
                        for proj in self.projectiles:
                            p_dist = math.hypot(tx - proj['x'], ty - proj['y'])
                            if p_dist < 150: proj_light += max(0, 200 - (p_dist * 1.5))
                        
                        if tile_val == TileType.WALL_TORCH.value: total_light = max(0, min(255, int(255 * self.global_flicker))) 
                        else: total_light = max(0, min(255, int((self.ambient_light + added_sunlight + torch_light + p_light + proj_light) * dist_shade)))
                        
                        off_clamped = max(0, min(TILE_SIZE - 1, int(off)))
                        
                        if self.in_interior: wall_slice = self.wall_textures["CAVE_ROCK"].subsurface(off_clamped, 0, 1, TILE_SIZE)
                        elif tile_val == TileType.DOOR.value: wall_slice = self.door_tex.subsurface(off_clamped, 0, 1, TILE_SIZE)
                        elif tile_val == TileType.DOOR_SILVER.value: wall_slice = self.door_silver_tex.subsurface(off_clamped, 0, 1, TILE_SIZE)
                        elif tile_val == TileType.DOOR_GOLD.value: wall_slice = self.door_gold_tex.subsurface(off_clamped, 0, 1, TILE_SIZE)
                        elif tile_val == TileType.STAIRS.value: wall_slice = self.wall_textures[TileType.STAIRS.value].subsurface(off_clamped, 0, 1, TILE_SIZE)
                        elif tile_val in self.wall_textures: wall_slice = self.wall_textures[tile_val].subsurface(off_clamped, 0, 1, TILE_SIZE)
                        else: wall_slice = self.wall_textures[TileType.WALL_BRICK.value].subsurface(off_clamped, 0, 1, TILE_SIZE)
                        
                        col_s = pygame.transform.scale(wall_slice, (int(WIDTH/NUM_RAYS)+1, wh))
                        m = max(0, min(255, total_light)) / 255.0
                        col_s.fill((int(m*255), int(m*255), int(m*255)), special_flags=pygame.BLEND_RGB_MULT)
                        self.screen.blit(col_s, (ray * (WIDTH / NUM_RAYS), HEIGHT // 2 - wh // 2))
                        break
            else:
                self.depth_buffer[ray] = MAX_DEPTH
