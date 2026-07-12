import json
import os

path = "adapters/hex64-qwen3-8b-final"
state_file = os.path.join(path, "trainer_state.json")

if not os.path.exists(state_file):
    print("trainer_state.json not found")
    exit(1)

with open(state_file, 'r') as f:
    state = json.load(f)

print(f"Max steps: {state.get('max_steps')}")
print(f"Total checkpoints: {len(state.get('log_history', []))}")
print("\nLast 5 training logs:")
for h in state['log_history'][-5:]:
    step = h.get('step', '?')
    loss = h.get('loss', 0)
    lr = h.get('learning_rate', 0)
    acc = h.get('mean_token_accuracy', 0)
    print(f"  Step {step}: loss={loss:.4f}, lr={lr:.2e}, acc={acc:.2%}")

# Check data size
train_file = os.path.join(path, "checkpoint-1000", "trainer_state.json")
if os.path.exists(train_file):
    with open(train_file, 'r') as f:
        train_state = json.load(f)
    print(f"\nTraining dataset info:")
    print(f"  Max steps: {train_state.get('max_steps')}")
    print(f"  Train batch size: {train_state.get('train_batch_size')}")
    print(f"  Save steps: {train_state.get('save_steps')}")
