import tkinter as tk
from tkinter import messagebox
import random

# GUI class implementing Banker's Algorithm with step-by-step visualization
class BankersAlgoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Banker's Algorithm: Simulation")
        self.root.geometry("1200x950")

        # Storage for all dynamic UI entry elements
        self.entries_allocation = []
        self.entries_max = []
        self.entries_need = []  
        self.entries_total = []
        self.entries_available = []
        self.request_entries = []
        self.entry_pid = None
        
        # Validation command to allow only integer input
        self.vcmd = (self.root.register(self.validate_input), '%P')

        self.setup_ui()

    def validate_input(self, new_value):
        """Allow only digit input for Entry widgets."""
        if new_value == "": return True
        return new_value.isdigit()

    # Main UI setup
    def setup_ui(self):
        # Top section for matrix size configuration
        config_frame = tk.Frame(self.root, pady=10, bg="#f0f0f0")
        config_frame.pack(fill="x")

        # Number of processes input
        tk.Label(config_frame, text="Processes (P):", bg="#f0f0f0").pack(side="left", padx=5)
        self.entry_n = tk.Entry(config_frame, width=5, validate="key", validatecommand=self.vcmd)
        self.entry_n.pack(side="left")
        self.entry_n.insert(0, "5")

        # Number of resources input
        tk.Label(config_frame, text="Resources (R):", bg="#f0f0f0").pack(side="left", padx=5)
        self.entry_m = tk.Entry(config_frame, width=5, validate="key", validatecommand=self.vcmd)
        self.entry_m.pack(side="left")
        self.entry_m.insert(0, "3")

        # Buttons to generate/reset/load data
        btn_gen = tk.Button(config_frame, text="Generate Table", command=self.generate_table, bg="#ddd")
        btn_gen.pack(side="left", padx=15)
        
        btn_rand = tk.Button(config_frame, text="Random Data", command=self.fill_random_data, bg="#FFD700")
        btn_rand.pack(side="right", padx=10)

        btn_reset = tk.Button(config_frame, text="Reset Fields", command=self.reset_fields, bg="#ffcccb")
        btn_reset.pack(side="right", padx=10)

        btn_sample = tk.Button(config_frame, text="Load Sample Data", command=self.load_sample_data, bg="#ADD8E6")
        btn_sample.pack(side="right", padx=10)

        # Scrollable matrix area container
        self.matrix_container = tk.Frame(self.root)
        self.matrix_container.pack(pady=5, expand=True, fill="both")
        self.setup_scrollable_area()

        # Bottom operation section for safety check and request handling
        ops_frame = tk.Frame(self.root, pady=5, relief="groove", bd=2)
        ops_frame.pack(side="bottom", fill="x", padx=10, pady=5)

        # Request input frame
        self.req_frame = tk.Frame(ops_frame, pady=5)
        self.req_frame.pack(fill="x")
        
        # Button to run safety algorithm
        btn_check = tk.Button(ops_frame, text="Check Safety & Show Steps", command=self.solve_and_log,
                              bg="#4CAF50", fg="white", font=("Arial", 11, "bold"))
        btn_check.pack(pady=5)
        
        self.result_label = tk.Label(ops_frame, text="Status: Ready", font=("Arial", 12, "bold"))
        self.result_label.pack(pady=2)

        # Split area: logs & Gantt chart
        bottom_split = tk.Frame(self.root, height=200)
        bottom_split.pack(side="bottom", fill="both", padx=10, pady=10)

        # Log window for detailed reasoning
        log_frame = tk.LabelFrame(bottom_split, text="Step-by-Step Reasoning Log", font=("Arial", 10, "bold"))
        log_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        self.log_text = tk.Text(log_frame, height=10, width=50, state="disabled", bg="#f9f9f9")
        log_scroll = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scroll.pack(side="right", fill="y")
        
        # Log text color tags
        self.log_text.tag_config("pass", foreground="green")
        self.log_text.tag_config("fail", foreground="red")
        self.log_text.tag_config("info", foreground="blue")

        # Gantt chart area to visualize safe sequence
        gantt_frame = tk.LabelFrame(bottom_split, text="Safe Sequence Gantt Chart", font=("Arial", 10, "bold"))
        gantt_frame.pack(side="right", fill="both", expand=True, padx=5)
        self.gantt_canvas = tk.Canvas(gantt_frame, bg="white", height=150)
        self.gantt_canvas.pack(fill="both", expand=True)

    # Create scrollable matrix area
    def setup_scrollable_area(self):
        for w in self.matrix_container.winfo_children(): w.destroy()

        self.matrix_canvas = tk.Canvas(self.matrix_container)
        scrollbar_y = tk.Scrollbar(self.matrix_container, orient="vertical", command=self.matrix_canvas.yview)
        scrollbar_x = tk.Scrollbar(self.matrix_container, orient="horizontal", command=self.matrix_canvas.xview)
        self.scrollable_frame = tk.Frame(self.matrix_canvas)

        # Update scroll region dynamically
        self.scrollable_frame.bind("<Configure>", lambda e: self.matrix_canvas.configure(scrollregion=self.matrix_canvas.bbox("all")))
        self.matrix_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.matrix_canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Canvas/grid layout
        self.matrix_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        self.matrix_container.grid_rowconfigure(0, weight=1)
        self.matrix_container.grid_columnconfigure(0, weight=1)

    # Generate Allocation, Max, Need, Total, Available tables dynamically
    def generate_table(self):
        self.scrollable_frame.destroy()
        self.setup_scrollable_area()
        for widget in self.req_frame.winfo_children(): widget.destroy()
        
        # Clear previous entries
        self.entries_allocation = []
        self.entries_max = []
        self.entries_need = []
        self.entries_total = []
        self.entries_available = []
        self.request_entries = []

        # Get P and R counts
        try:
            n = int(self.entry_n.get())
            m = int(self.entry_m.get())
        except ValueError:
            return

        # Table headers
        tk.Label(self.scrollable_frame, text="Process", font="bold").grid(row=0, column=0, rowspan=2, padx=5)
        tk.Label(self.scrollable_frame, text="Allocation", font="bold").grid(row=0, column=1, columnspan=m, pady=5)
        tk.Label(self.scrollable_frame, text="Max", font="bold").grid(row=0, column=m+2, columnspan=m, pady=5)
        tk.Label(self.scrollable_frame, text="Need (Calc)", font="bold", fg="gray").grid(row=0, column=(2*m)+3, columnspan=m, pady=5)

        # Resource column labels
        for j in range(m):
            tk.Label(self.scrollable_frame, text=f"R{j}", font=("Arial", 8, "italic")).grid(row=1, column=1+j)
            tk.Label(self.scrollable_frame, text=f"R{j}", font=("Arial", 8, "italic")).grid(row=1, column=m+2+j)
            tk.Label(self.scrollable_frame, text=f"R{j}", font=("Arial", 8, "italic"), fg="gray").grid(row=1, column=(2*m)+3+j)

        # Separators for readability
        tk.Label(self.scrollable_frame, text="|", font="bold").grid(row=0, column=m+1, rowspan=n+2)
        tk.Label(self.scrollable_frame, text="|", font="bold").grid(row=0, column=(2*m)+2, rowspan=n+2)

        # Process rows
        for i in range(n):
            row_idx = i + 2
            tk.Label(self.scrollable_frame, text=f"P{i}", font="bold").grid(row=row_idx, column=0, padx=5)
            
            # Allocation matrix inputs
            row_alloc = []
            for j in range(m):
                e = tk.Entry(self.scrollable_frame, width=5, justify="center", validate="key", validatecommand=self.vcmd)
                e.grid(row=row_idx, column=1+j, padx=2, pady=2)
                row_alloc.append(e)
            self.entries_allocation.append(row_alloc)

            tk.Label(self.scrollable_frame, text="|").grid(row=row_idx, column=m+1)

            # Max matrix inputs
            row_max = []
            for j in range(m):
                e = tk.Entry(self.scrollable_frame, width=5, justify="center", validate="key", validatecommand=self.vcmd)
                e.grid(row=row_idx, column=m+2+j, padx=2, pady=2)
                row_max.append(e)
            self.entries_max.append(row_max)

            tk.Label(self.scrollable_frame, text="|").grid(row=row_idx, column=(2*m)+2)

            # Need matrix (auto-calculated, read-only)
            row_need = []
            for j in range(m):
                e = tk.Entry(self.scrollable_frame, width=5, justify="center", bg="#e0e0e0", fg="#333")
                e.grid(row=row_idx, column=(2*m)+3+j, padx=2, pady=2)
                row_need.append(e)
            self.entries_need.append(row_need)

        # Total resources row
        total_row = n + 4
        tk.Label(self.scrollable_frame, text="Total Resources:", font="bold", fg="blue").grid(row=total_row, column=0, padx=5, sticky="e")
        
        for j in range(m):
            tk.Label(self.scrollable_frame, text=f"R{j}", font=("Arial", 8, "italic")).grid(row=total_row-1, column=1+j)
            e = tk.Entry(self.scrollable_frame, width=5, justify="center", validate="key",
                         validatecommand=self.vcmd, bg="#e6f2ff")
            e.grid(row=total_row, column=1+j, padx=2)
            self.entries_total.append(e)

        btn_calc_avail = tk.Button(self.scrollable_frame, text="Calc Available ↓", command=self.calculate_available,
                                   bg="#ADD8E6", font=("Arial", 9, "bold"))
        btn_calc_avail.grid(row=total_row, column=m+2, columnspan=2, sticky="w", padx=10)

        # Available vector inputs
        avail_row = n + 6
        tk.Label(self.scrollable_frame, text="Available:", font="bold").grid(row=avail_row, column=0, padx=5, sticky="e")

        for j in range(m):
            tk.Label(self.scrollable_frame, text=f"R{j}", font=("Arial", 8, "italic")).grid(row=avail_row-1, column=1+j)
            e = tk.Entry(self.scrollable_frame, width=5, justify="center", validate="key", validatecommand=self.vcmd)
            e.grid(row=avail_row, column=1+j, padx=2)
            self.entries_available.append(e)

        # Request row UI
        tk.Label(self.req_frame, text="Make a Request:", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        tk.Label(self.req_frame, text="Process ID:").pack(side="left")
        self.entry_pid = tk.Entry(self.req_frame, width=5, justify="center", validate="key", validatecommand=self.vcmd)
        self.entry_pid.pack(side="left", padx=5)
        tk.Label(self.req_frame, text="Request Vector:").pack(side="left", padx=5)
        for j in range(m):
            e = tk.Entry(self.req_frame, width=5, justify="center", validate="key", validatecommand=self.vcmd)
            e.pack(side="left", padx=2)
            self.request_entries.append(e)

        btn_req = tk.Button(self.req_frame, text="Submit Request", command=self.handle_request,
                            bg="#FF9800", fg="white")
        btn_req.pack(side="left", padx=15)

    # Compute Available = Total - Allocation sums
    def calculate_available(self):
        """Computes available resources from total and existing allocation."""
        try:
            totals = []
            for e in self.entries_total:
                val = e.get()
                if not val:
                    messagebox.showerror("Error", "Please enter Total Resources first.")
                    return
                totals.append(int(val))
            
            m = len(totals)
            n = len(self.entries_allocation)
            
            alloc_sum = [0] * m
            for i in range(n):
                for j in range(m):
                    val = self.entries_allocation[i][j].get()
                    alloc_sum[j] += int(val) if val else 0
            
            # Fill computed available vector
            for j in range(m):
                avail_val = totals[j] - alloc_sum[j]
                if avail_val < 0:
                    messagebox.showwarning("Warning", f"Allocation for R{j} exceeds Total!")
                
                self.entries_available[j].delete(0, tk.END)
                self.entries_available[j].insert(0, str(avail_val))
                
        except ValueError:
            messagebox.showerror("Error", "Invalid input detected.")

    # Append messages to log panel
    def write_log(self, message, tag=None):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    # Main safety algorithm and logging
    def solve_and_log(self):
        """Runs Banker's Safety algorithm and logs steps."""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
        
        state = self.get_state_from_ui()
        if not state: return
        alloc, max_mat, avail, need, n, m = state

        # Update Need matrix UI
        for i in range(n):
            for j in range(m):
                self.entries_need[i][j].config(state="normal")
                self.entries_need[i][j].delete(0, tk.END)
                self.entries_need[i][j].insert(0, str(need[i][j]))
                self.entries_need[i][j].config(state="readonly")

        self.write_log("--- Starting Safety Algorithm ---", "info")
        self.write_log(f"Initial Available: {avail}\n")

        # Safety algorithm core
        work = avail[:]
        finish = [False] * n
        safe_seq = []
        count = 0
        
        while count < n:
            found = False
            for p in range(n):
                if not finish[p]:
                    is_possible = True
                    for j in range(m):
                        if need[p][j] > work[j]:
                            is_possible = False
                            break
                    
                    if is_possible:
                        self.write_log(f"P{p} Check: Need {need[p]} <= Work {work}? YES.", "pass")
                        for k in range(m): work[k] += alloc[p][k]
                        self.write_log(f"   -> P{p} finishes. New Work: {work}")
                        
                        safe_seq.append(f"P{p}")
                        finish[p] = True
                        found = True
                        count += 1
                    else:
                        pass
            
            if not found:
                self.write_log(f"\nNo process can be satisfied with Work {work}.", "fail")
                break
        
        # Final result handling
        if count == n:
            self.result_label.config(text=f"SAFE STATE. Sequence: {' -> '.join(safe_seq)}", fg="green")
            self.write_log(f"\nSystem is SAFE. Sequence: {safe_seq}", "pass")
            self.draw_gantt_chart(safe_seq)
        else:
            self.result_label.config(text="UNSAFE (Deadlock Detected)", fg="red")
            self.write_log(f"\nSystem is UNSAFE. Deadlock detected.", "fail")
            self.gantt_canvas.delete("all")

    # Extract state from UI into Python structures
    def get_state_from_ui(self):
        try:
            alloc = [[int(e.get() if e.get() else 0) for e in row] for row in self.entries_allocation]
            max_mat = [[int(e.get() if e.get() else 0) for e in row] for row in self.entries_max]
            avail = [int(e.get() if e.get() else 0) for e in self.entries_available]
            n = len(alloc)
            m = len(avail)

            # Compute Need matrix
            need = []
            for i in range(n):
                row = []
                for j in range(m):
                    n_val = max_mat[i][j] - alloc[i][j]
                    if n_val < 0: 
                        messagebox.showerror("Error", f"P{i}: Allocation cannot exceed Max!")
                        return None
                    row.append(n_val)
                need.append(row)
            return alloc, max_mat, avail, need, n, m
        except ValueError:
            messagebox.showerror("Input Error", "Invalid numbers detected.")
            return None

    # Handle resource request from a process
    def handle_request(self):
        try:
            pid = int(self.entry_pid.get())
            req_vec = [int(e.get() if e.get() else 0) for e in self.request_entries]
        except ValueError:
            messagebox.showerror("Error", "Invalid Request Inputs")
            return

        state = self.get_state_from_ui()
        if not state: return
        alloc, max_mat, avail, need, n, m = state

        if pid < 0 or pid >= n:
            messagebox.showerror("Error", "Invalid Process ID")
            return

        # Logging the request
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
        self.write_log(f"--- Handling Request for P{pid}: {req_vec} ---", "info")

        # Check if request exceeds need
        for j in range(m):
            if req_vec[j] > need[pid][j]:
                self.write_log(f"Error: Request {req_vec} > Need {need[pid]}", "fail")
                messagebox.showerror("Error", "Request exceeds Need")
                return
        
        # Check if request exceeds available
        for j in range(m):
            if req_vec[j] > avail[j]:
                self.write_log(f"Wait: Request {req_vec} > Available {avail}", "fail")
                messagebox.showwarning("Wait", f"Resources not available. P{pid} must wait.")
                return

        # Provisional allocation test
        self.write_log("Conditions met. Attempting provisional allocation...", "info")
        new_avail = avail[:]
        new_alloc = [row[:] for row in alloc]
        
        for j in range(m):
            new_avail[j] -= req_vec[j]
            new_alloc[pid][j] += req_vec[j]
        
        # Recalculate need after provisional allocation
        new_need = []
        for i in range(n):
            row = []
            for j in range(m):
                row.append(max_mat[i][j] - new_alloc[i][j])
            new_need.append(row)

        # Safety check after provisional allocation
        work = new_avail[:]
        finish = [False] * n
        safe_seq = []
        count = 0
        while count < n:
            found = False
            for p in range(n):
                if not finish[p]:
                    if all(new_need[p][j] <= work[j] for j in range(m)):
                        for k in range(m): work[k] += new_alloc[p][k]
                        safe_seq.append(f"P{p}")
                        finish[p] = True
                        found = True
                        count += 1
            if not found: break
        
        # Grant or deny request
        if count == n:
            self.write_log(f"Request Granted. Safe Sequence: {safe_seq}", "pass")
            self.result_label.config(text="Request GRANTED", fg="green")
            self.draw_gantt_chart(safe_seq)
            
            # Update UI to new state
            for j in range(m):
                self.entries_available[j].delete(0, tk.END)
                self.entries_available[j].insert(0, str(new_avail[j]))
                self.entries_allocation[pid][j].delete(0, tk.END)
                self.entries_allocation[pid][j].insert(0, str(new_alloc[pid][j]))
            
            # Re-run safety algorithm
            self.solve_and_log()
        else:
            self.write_log("Request Denied. Resulting state would be UNSAFE.", "fail")
            self.result_label.config(text="Request DENIED", fg="red")
            messagebox.showwarning("Unsafe", "Request Denied.\nSystem would enter Unsafe state.")

    # Draw graphical safe sequence (Gantt chart)
    def draw_gantt_chart(self, sequence):
        self.gantt_canvas.delete("all")
        if not sequence: return
        start_x, y, w, h = 20, 40, 60, 40
        for i, pid in enumerate(sequence):
            self.gantt_canvas.create_rectangle(start_x, y, start_x + w, y + h, fill="#90EE90", outline="black")
            self.gantt_canvas.create_text(start_x + w/2, y + h/2, text=pid, font=("Arial", 10, "bold"))
            if i < len(sequence) - 1:
                self.gantt_canvas.create_line(start_x + w, y + h/2, start_x + w + 20, y + h/2, arrow=tk.LAST)
                start_x += w + 20
            else: start_x += w

    # Fill matrices with valid random data
    def fill_random_data(self):
        self.generate_table()
        try:
            n = int(self.entry_n.get())
            m = int(self.entry_m.get())
            
            alloc_sums = [0] * m
            
            # Random allocation and max values
            for i in range(n):
                for j in range(m):
                    max_val = random.randint(1, 15)
                    alloc_val = random.randint(0, max_val)
                    self.entries_max[i][j].insert(0, str(max_val))
                    self.entries_allocation[i][j].insert(0, str(alloc_val))
                    alloc_sums[j] += alloc_val
            
            # Available and Total (consistent)
            for j in range(m):
                avail_val = random.randint(1, 10)
                self.entries_available[j].insert(0, str(avail_val))
                total_val = alloc_sums[j] + avail_val
                self.entries_total[j].insert(0, str(total_val))
                
        except ValueError: pass

    # Load predefined sample data (from popular OS textbook example)
    def load_sample_data(self):
        self.entry_n.delete(0, tk.END); self.entry_n.insert(0, "5")
        self.entry_m.delete(0, tk.END); self.entry_m.insert(0, "3")
        self.generate_table()
        alloc_data = [[0,1,0], [2,0,0], [3,0,2], [2,1,1], [0,0,2]]
        max_data   = [[7,5,3], [3,2,2], [9,0,2], [2,2,2], [4,3,3]]
        avail_data = [3, 3, 2]
        
        totals = [10, 5, 7]  # Pre-computed totals for sample

        # Fill sample matrices
        for i in range(5):
            for j in range(3):
                self.entries_allocation[i][j].insert(0, alloc_data[i][j])
                self.entries_max[i][j].insert(0, max_data[i][j])
        
        for j in range(3):
            self.entries_available[j].insert(0, avail_data[j])
            self.entries_total[j].insert(0, totals[j])
            
    def reset_fields(self):
        """Clears the table by regenerating it."""
        self.generate_table()

# Main application run
if __name__ == "__main__":
    root = tk.Tk()
    app = BankersAlgoGUI(root)
    root.mainloop()
