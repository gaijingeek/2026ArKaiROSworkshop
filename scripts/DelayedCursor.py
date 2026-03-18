import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, clear_output
import ipywidgets as widgets
from collections import deque

def improved_cursor_demo():
    """
    Improved cursor demo showing movement history
    """
    
    output = widgets.Output()
    
    # Store longer history for visualization
    state = {
        'input_history': deque(maxlen=500),
        'output_history': deque(maxlen=500),
        'time_step': 0
    }
    
    @widgets.interact(
        cursor=widgets.FloatSlider(
            min=0, max=100, value=50, step=1,
            description='Move Cursor:', 
            continuous_update=True,
            layout=widgets.Layout(width='600px'),
            readout_format='.0f'
        ),
        delay_steps=widgets.IntSlider(
            min=0, max=20, value=0,
            description='Delay (steps):',
            layout=widgets.Layout(width='400px')
        ),
        noise=widgets.FloatSlider(
            min=0, max=5, value=0, step=0.5,
            description='Noise Level:',
            layout=widgets.Layout(width='400px')
        )
    )
    def move_cursor(cursor, delay_steps, noise):
        # Update time step
        state['time_step'] += 1
        
        # Add current input to history
        state['input_history'].append(cursor)
        
        # Get delayed position (exact copy from past)
        if delay_steps > 0 and len(state['input_history']) > delay_steps:
            delayed_pos = state['input_history'][-(delay_steps+1)]
        else:
            delayed_pos = cursor
        
        # Add noise if specified
        output_pos = delayed_pos
        if noise > 0:
            output_pos = delayed_pos + np.random.normal(0, noise)
            output_pos = np.clip(output_pos, 0, 100)
        
        # Store output
        state['output_history'].append(output_pos)
        
        with output:
            clear_output(wait=True)
            
            # Create two-panel plot
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), height_ratios=[1, 1])
            
            # Panel 1: Current positions
            ax1.set_xlim(-5, 105)
            ax1.set_ylim(-0.5, 0.5)
            
            # Background scale
            for pos in [0, 25, 50, 75, 100]:
                ax1.axvline(x=pos, color='gray', linestyle=':', alpha=0.2)
            
            # Current positions
            ax1.scatter(cursor, 0, s=300, c='green', marker='v', 
                       alpha=0.7, label=f'Input: {cursor:.0f}', zorder=5)
            ax1.scatter(output_pos, 0, s=300, c='red', marker='^', 
                       alpha=0.7, label=f'Output: {output_pos:.0f}', zorder=5)
            
            # Connection line
            ax1.plot([cursor, output_pos], [0, 0], 'k--', alpha=0.3, linewidth=1)
            
            ax1.set_ylabel('Current', fontsize=11)
            ax1.set_yticks([])
            ax1.legend(loc='upper right')
            ax1.set_title(f'Real-time Cursor Tracking (Delay: {delay_steps} steps, Noise: {noise:.1f})',
                         fontsize=12, fontweight='bold')
            
            # Panel 2: History trace
            ax2.set_xlim(-5, 105)
            ax2.set_ylim(-1, max(20, len(state['input_history']) + 1))
            
            # Plot histories
            n_points = min(len(state['input_history']), len(state['output_history']))
            if n_points > 1:
                time_points = list(range(n_points))
                
                # Input history (green)
                input_vals = list(state['input_history'])[-n_points:]
                ax2.plot(input_vals, time_points, 'g-', alpha=0.6, linewidth=2, label='Input')
                ax2.scatter(input_vals[-1], time_points[-1], c='green', s=100, zorder=5)
                
                # Output history (red)
                output_vals = list(state['output_history'])[-n_points:]
                ax2.plot(output_vals, time_points, 'r-', alpha=0.6, linewidth=2, label='Output')
                ax2.scatter(output_vals[-1], time_points[-1], c='red', s=100, zorder=5)
                
                # Show delay visually
                if delay_steps > 0 and n_points > delay_steps:
                    # Connect corresponding points
                    for i in range(n_points - delay_steps, n_points, 3):
                        ax2.plot([input_vals[i], output_vals[i + delay_steps - 1]], 
                                [time_points[i], time_points[i + delay_steps - 1]], 
                                'k:', alpha=0.2, linewidth=0.5)
            
            ax2.set_xlabel('Position', fontsize=11)
            ax2.set_ylabel('Time (steps ago)', fontsize=11)
            ax2.invert_yaxis()
            ax2.legend(loc='upper right')
            ax2.grid(True, alpha=0.2)
            
            # Background scale
            for pos in [0, 25, 50, 75, 100]:
                ax2.axvline(x=pos, color='gray', linestyle=':', alpha=0.2)
            
            plt.tight_layout()
            plt.show()
            
            # Statistics
            if len(state['input_history']) > delay_steps:
                expected_output = state['input_history'][-delay_steps-1] if delay_steps > 0 else cursor
                actual_error = abs(output_pos - expected_output)
                tracking_error = abs(cursor - output_pos)
                
                print(f"📊 Statistics:")
                print(f"  • Current Input: {cursor:.0f}")
                print(f"  • Expected Output (delayed): {expected_output:.0f}")
                print(f"  • Actual Output (with noise): {output_pos:.0f}")
                print(f"  • Noise Error: {actual_error:.1f}")
                print(f"  • Total Tracking Error: {tracking_error:.1f}")
    
    display(output)

# Run the improved demo
improved_cursor_demo()