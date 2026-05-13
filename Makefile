SKILLS_DIR := $(CURDIR)/skills
TARGET_DIR := $(HOME)/.claude/skills
HOOKS_SRC := $(CURDIR)/scripts/hooks
HOOKS_DST := $(CURDIR)/.git/hooks

SKILL_DIRS := $(wildcard $(SKILLS_DIR)/*)

.PHONY: install uninstall list install-hooks check-pii

install: install-hooks
	@mkdir -p "$(TARGET_DIR)"
	@for skill in $(SKILL_DIRS); do \
		name=$$(basename "$$skill"); \
		target="$(TARGET_DIR)/$$name"; \
		if [ -L "$$target" ] && [ "$$(readlink "$$target")" = "$$skill" ]; then \
			echo "  ok  $$name (already linked)"; \
		elif [ -e "$$target" ]; then \
			echo "  SKIP  $$name — already exists at $$target (not overwriting)"; \
		else \
			ln -s "$$skill" "$$target"; \
			echo "  link  $$name → $$skill"; \
		fi; \
	done
	@echo ""
	@echo "Done. Skills are available as /skill-name in all projects."

uninstall:
	@for skill in $(SKILL_DIRS); do \
		name=$$(basename "$$skill"); \
		target="$(TARGET_DIR)/$$name"; \
		if [ -L "$$target" ] && [ "$$(readlink "$$target")" = "$$skill" ]; then \
			rm "$$target"; \
			echo "  unlink  $$name"; \
		elif [ -e "$$target" ]; then \
			echo "  SKIP  $$name — exists but not our symlink (not touching)"; \
		else \
			echo "  ok  $$name (not installed)"; \
		fi; \
	done

install-hooks:
	@if [ ! -d "$(HOOKS_DST)" ]; then \
		echo "  SKIP  hooks — $(HOOKS_DST) doesn't exist (not a git checkout?)"; \
	else \
		for hook in $(HOOKS_SRC)/*; do \
			name=$$(basename "$$hook"); \
			target="$(HOOKS_DST)/$$name"; \
			if [ -L "$$target" ] && [ "$$(readlink "$$target")" = "$$hook" ]; then \
				echo "  ok  hook $$name (already linked)"; \
			elif [ -e "$$target" ]; then \
				echo "  SKIP  hook $$name — already exists at $$target (not overwriting)"; \
			else \
				ln -s "$$hook" "$$target"; \
				echo "  link  hook $$name → $$hook"; \
			fi; \
		done; \
	fi

check-pii:
	@bash $(CURDIR)/scripts/check-pii.sh --all

list:
	@echo "Skills in this repo:"
	@for skill in $(SKILL_DIRS); do \
		name=$$(basename "$$skill"); \
		desc=$$(awk '/^description:/{sub(/^description: */, ""); print; exit}' "$$skill/SKILL.md" 2>/dev/null || echo "(no description)"); \
		echo "  $$name — $$desc"; \
	done
	@echo ""
	@echo "Installed symlinks in $(TARGET_DIR):"
	@for skill in $(SKILL_DIRS); do \
		name=$$(basename "$$skill"); \
		target="$(TARGET_DIR)/$$name"; \
		if [ -L "$$target" ] && [ "$$(readlink "$$target")" = "$$skill" ]; then \
			echo "  ✓ $$name"; \
		elif [ -e "$$target" ]; then \
			echo "  ✗ $$name (exists, not our link)"; \
		else \
			echo "  - $$name (not installed)"; \
		fi; \
	done
