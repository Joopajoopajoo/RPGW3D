import pygame
from settings import *

class Inventory:
    def __init__(self, icons_dict, sfx_dict):
        self.slots = [None] * 16 
        self.visible = False
        self.rect = pygame.Rect(0, 0, 340, 340) 
        self.icons = icons_dict
        self.sfx = sfx_dict
        self.cols, self.rows = 4, 4
        self.slot_size, self.margin = 60, 15
        
        # Center layout dimensions relative to screen configurations
        self.rect.center = (WIDTH // 2, HEIGHT // 2 - 40)
        
    def toggle(self):
        self.visible = not self.visible
        if self.visible and self.sfx.get("door"): self.sfx["door"].play()
            
    def add_item(self, name, qty, item_type, desc, health=0, mana=0):
        for slot in self.slots:
            if slot and slot["name"] == name and slot["type"] not in ["weapon", "artifact"]:
                slot["qty"] += qty
                return True
        # FIXED: Added the critical return statement to break the infinite boot loop!
        for i in range(len(self.slots)):
            if self.slots[i] is None:
                self.slots[i] = {"name": name, "qty": qty, "type": item_type, "desc": desc, "health": health, "mana": mana, "equipped": False}
                return True
        return False

    def get_icon_for_item(self, item):
        n = item["name"]
        icons = {
            "Sword": "sword", 
            "Brass Key": "key",              
            "Silver Key": "key_silver",      
            "Gold Key": "key_gold",          
            "Rusty Key": "key_dungeon",      
            "Rusty Key 2": "key_rusty_2",    
            "Health Potion": "health_potion", 
            "Mana Potion": "mana_potion", 
            "Mystic Artifact": "artifact", 
            "Unlit Torch": "unlit_torch", 
            "Lit Torch": "lit_torch", 
            "Mystic Staff": "staff"
        }
        icon_key = icons.get(n)
        if icon_key: return self.icons.get(icon_key)
        return None

    def find_item_by_name(self, name):
        for i, slot in enumerate(self.slots):
            if slot and slot["name"] == name: return i, slot
        return None, None

    def get_equipped_weapon(self):
        for slot in self.slots:
            if slot and slot["type"] == "weapon" and slot.get("equipped"): return slot
        return None

    def get_slot_at(self, pos):
        if not self.visible: return None
        mx, my = pos
        for i in range(16):
            row, col = i // self.cols, i % self.cols
            sx = self.rect.x + 25 + col * (self.slot_size + self.margin)
            sy = self.rect.y + 50 + row * (self.slot_size + self.margin)
            if pygame.Rect(sx, sy, self.slot_size, self.slot_size).collidepoint(mx, my): return i
        return None

    def draw(self, screen, mouse_pos, font):
        if not self.visible: return
        sw, sh = screen.get_size()
        
        self.rect.center = (sw // 2, sh // 2 - 40)
        
        # Solid base rendering to avoid driver compatibility alpha bugs
        pygame.draw.rect(screen, (30, 30, 35), self.rect)
        pygame.draw.rect(screen, (200, 180, 100), self.rect, 3)
        
        for i in range(16):
            row, col = i // self.cols, i % self.cols
            sx = self.rect.x + 25 + col * (self.slot_size + self.margin)
            sy = self.rect.y + 50 + row * (self.slot_size + self.margin)
            s_rect = pygame.Rect(sx, sy, self.slot_size, self.slot_size)
            pygame.draw.rect(screen, (60, 60, 65), s_rect)
            pygame.draw.rect(screen, (100, 100, 110), s_rect, 2)
            
            slot = self.slots[i]
            if slot:
                icon = self.get_icon_for_item(slot)
                if icon: 
                    icon_s = pygame.transform.scale(icon, (self.slot_size - 10, self.slot_size - 10))
                    screen.blit(icon_s, (sx + 5, sy + 5))
                
                if slot.get("qty", 1) > 1:
                    q_txt = font.render(str(slot["qty"]), True, (255, 255, 255))
                    screen.blit(q_txt, (sx + self.slot_size - 15, sy + self.slot_size - 20))
                    
                if slot.get("equipped"):
                    pygame.draw.rect(screen, (50, 255, 50), s_rect, 2)
                    eq_txt = font.render("E", True, (50, 255, 50))
                    screen.blit(eq_txt, (sx + 5, sy + self.slot_size - 20))
                    
                if s_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, (200, 200, 200), s_rect, 2)
                    
        # --- FEATURE: Dynamic tooltips drawn directly alongside your mouse pointer ---
        hovered = self.get_slot_at(mouse_pos)
        if hovered is not None and self.slots[hovered]:
            mx, my = mouse_pos
            desc_rect = pygame.Rect(mx + 15, my + 15, 220, 55)
            
            # Boundary checks to prevent info tooltips from wandering off the window boundaries
            if desc_rect.right > sw: desc_rect.x = mx - 235
            if desc_rect.bottom > sh: desc_rect.y = my - 65
            
            pygame.draw.rect(screen, (20, 20, 25), desc_rect)
            pygame.draw.rect(screen, (200, 180, 100), desc_rect, 2)
            name_txt = font.render(self.slots[hovered]["name"], True, (255, 215, 0))
            desc_txt = font.render(self.slots[hovered].get("desc", ""), True, (200, 200, 200))
            screen.blit(name_txt, (desc_rect.x + 10, desc_rect.y + 7))
            screen.blit(desc_txt, (desc_rect.x + 10, desc_rect.y + 28))
