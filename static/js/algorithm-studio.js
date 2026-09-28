(()=>{'use strict';
const $=id=>document.getElementById(id);
const topics=[
{id:'bubble',name:'Bubble Sort',kind:'algorithm',group:'Sorting',icon:'bi-bar-chart-steps',best:'O(n)',avg:'O(n²)',worst:'O(n²)',space:'O(1)',desc:'Repeatedly compare adjacent values and move larger values right.',steps:['Compare adjacent values.','Swap when the left value is larger.','Repeat until a pass makes no swaps.']},
{id:'selection',name:'Selection Sort',kind:'algorithm',group:'Sorting',icon:'bi-sort-down',best:'O(n²)',avg:'O(n²)',worst:'O(n²)',space:'O(1)',desc:'Select the smallest remaining value and place it next.',steps:['Find the minimum in the unsorted suffix.','Swap it into the current position.','Advance the sorted boundary.']},
{id:'insertion',name:'Insertion Sort',kind:'algorithm',group:'Sorting',icon:'bi-list-ol',best:'O(n)',avg:'O(n²)',worst:'O(n²)',space:'O(1)',desc:'Insert each value into its correct position in the sorted prefix.',steps:['Take the next key.','Shift larger values right.','Insert the key into the gap.']},
{id:'merge',name:'Merge Sort',kind:'algorithm',group:'Sorting',icon:'bi-diagram-2',best:'O(n log n)',avg:'O(n log n)',worst:'O(n log n)',space:'O(n)',desc:'Divide the array, sort each half, then merge.',steps:['Split until single elements remain.','Merge ordered halves.','Return the combined result.']},
{id:'quick',name:'Quick Sort',kind:'algorithm',group:'Sorting',icon:'bi-lightning',best:'O(n log n)',avg:'O(n log n)',worst:'O(n²)',space:'O(log n)',desc:'Partition values around a pivot and recursively sort both sides.',steps:['Choose a pivot.','Partition smaller and larger values.','Recursively process both partitions.']},
{id:'linear',name:'Linear Search',kind:'algorithm',group:'Searching',icon:'bi-search',best:'O(1)',avg:'O(n)',worst:'O(n)',space:'O(1)',desc:'Inspect values from left to right until the target is found.',steps:['Start at index zero.','Compare the current value.','Stop on match or at the end.']},
{id:'binary',name:'Binary Search',kind:'algorithm',group:'Searching',icon:'bi-arrows-collapse',best:'O(1)',avg:'O(log n)',worst:'O(log n)',space:'O(1)',desc:'Halve a sorted search range after every comparison.',steps:['Keep low and high boundaries.','Compare the middle value.','Discard the impossible half.']},
{id:'array',name:'Dynamic Array',kind:'structure',group:'Linear',icon:'bi-braces',best:'O(1)',avg:'O(1)',worst:'O(n)',space:'O(n)',desc:'Contiguous indexed storage with amortized growth.',steps:['Read by index in constant time.','Append into available capacity.','Resize and copy when capacity is full.']},
{id:'linked',name:'Linked List',kind:'structure',group:'Linear',icon:'bi-link-45deg',best:'O(1)',avg:'O(n)',worst:'O(n)',space:'O(n)',desc:'Nodes connected through references support flexible insertion.',steps:['Store data in a node.','Link the node to its successor.','Traverse from the head.']},
{id:'stack',name:'Stack',kind:'structure',group:'Linear',icon:'bi-layers',best:'O(1)',avg:'O(1)',worst:'O(1)',space:'O(n)',desc:'Last-in, first-out storage using push and pop.',steps:['Push adds to the top.','Pop removes the top.','Peek reads without removing.']},
{id:'queue',name:'Queue',kind:'structure',group:'Linear',icon:'bi-list-nested',best:'O(1)',avg:'O(1)',worst:'O(1)',space:'O(n)',desc:'First-in, first-out storage using enqueue and dequeue.',steps:['Enqueue at the rear.','Dequeue from the front.','Track both ends efficiently.']},
{id:'hash',name:'Hash Table',kind:'structure',group:'Hashing',icon:'bi-grid-3x3-gap',best:'O(1)',avg:'O(1)',worst:'O(n)',space:'O(n)',desc:'Map keys to buckets for near constant-time access.',steps:['Hash the key.','Find the bucket.','Resolve collisions safely.']},
{id:'bst',name:'Binary Search Tree',kind:'structure',group:'Trees',icon:'bi-diagram-3',best:'O(log n)',avg:'O(log n)',worst:'O(n)',space:'O(n)',desc:'Ordered tree with smaller values left and larger values right.',steps:['Compare with the current node.','Move left or right.','Insert or return on match.']},
{id:'heap',name:'Binary Heap',kind:'structure',group:'Trees',icon:'bi-triangle',best:'O(1)',avg:'O(log n)',worst:'O(log n)',space:'O(n)',desc:'Complete tree optimized for priority access.',steps:['Insert at the end.','Bubble upward to restore order.','Heapify downward after removal.']},
{id:'bfs',name:'Breadth-First Search',kind:'algorithm',group:'Graphs',icon:'bi-bounding-box-circles',best:'O(V+E)',avg:'O(V+E)',worst:'O(V+E)',space:'O(V)',desc:'Explore a graph level by level using a queue.',steps:['Enqueue the start node.','Visit every unvisited neighbor.','Continue until the queue is empty.']},
{id:'dfs',name:'Depth-First Search',kind:'algorithm',group:'Graphs',icon:'bi-signpost-split',best:'O(V+E)',avg:'O(V+E)',worst:'O(V+E)',space:'O(V)',desc:'Explore deeply before backtracking.',steps:['Visit the current node.','Recurse into an unvisited neighbor.','Backtrack when no edge remains.']},
{id:'dijkstra',name:"Dijkstra's Algorithm",kind:'algorithm',group:'Graphs',icon:'bi-bezier2',best:'O((V+E) log V)',avg:'O((V+E) log V)',worst:'O((V+E) log V)',space:'O(V)',desc:'Find shortest paths with non-negative weights.',steps:['Set the source distance to zero.','Extract the closest unsettled vertex.','Relax each outgoing edge.']},
{id:'dp',name:'Dynamic Programming',kind:'algorithm',group:'Optimization',icon:'bi-table',best:'O(n)',avg:'O(n)',worst:'O(n)',space:'O(n)',desc:'Store overlapping subproblem results and reuse them.',steps:['Define the state.','Write the transition.','Build answers from smaller states.']}
];
topics.push(
{id:'deque',name:'Deque',kind:'structure',group:'Linear',icon:'bi-arrow-left-right',best:'O(1)',avg:'O(1)',worst:'O(1)',space:'O(n)',desc:'Insert and remove values efficiently at both ends.',steps:['Maintain front and rear ends.','Push at either end.','Pop from either end.']},
{id:'trie',name:'Trie',kind:'structure',group:'Trees',icon:'bi-diagram-3',best:'O(L)',avg:'O(L)',worst:'O(L)',space:'O(total characters)',desc:'Prefix tree for fast word insertion and lookup.',steps:['Start at the root.','Follow or create one edge per character.','Mark complete words.']},
{id:'unionfind',name:'Disjoint Set Union',kind:'structure',group:'Graphs',icon:'bi-share',best:'O(α(n))',avg:'O(α(n))',worst:'O(α(n))',space:'O(n)',desc:'Track connected components with path compression and union by size.',steps:['Create one parent per item.','Compress paths during find.','Join smaller roots under larger roots.']},
{id:'counting',name:'Counting Sort',kind:'algorithm',group:'Sorting',icon:'bi-bar-chart',best:'O(n+k)',avg:'O(n+k)',worst:'O(n+k)',space:'O(k)',desc:'Count bounded integer keys and rebuild them in order.',steps:['Count every value.','Scan counts from low to high.','Write each value by its frequency.']},
{id:'heapsort',name:'Heap Sort',kind:'algorithm',group:'Sorting',icon:'bi-triangle',best:'O(n log n)',avg:'O(n log n)',worst:'O(n log n)',space:'O(1)',desc:'Build a max heap and repeatedly move its root to the sorted suffix.',steps:['Build a max heap.','Swap the root with the last item.','Restore the heap on the remaining prefix.']},
{id:'bellman',name:'Bellman–Ford',kind:'algorithm',group:'Graphs',icon:'bi-signpost',best:'O(VE)',avg:'O(VE)',worst:'O(VE)',space:'O(V)',desc:'Shortest paths with negative edges and cycle detection.',steps:['Initialize source distance.','Relax every edge V−1 times.','Check once more for a negative cycle.']},
{id:'kruskal',name:"Kruskal's MST",kind:'algorithm',group:'Graphs',icon:'bi-bezier',best:'O(E log E)',avg:'O(E log E)',worst:'O(E log E)',space:'O(V)',desc:'Build a minimum spanning tree by accepting the lightest safe edges.',steps:['Sort edges by weight.','Use DSU to reject cycles.','Stop after V−1 accepted edges.']},
{id:'lcs',name:'Longest Common Subsequence',kind:'algorithm',group:'Dynamic Programming',icon:'bi-grid',best:'O(mn)',avg:'O(mn)',worst:'O(mn)',space:'O(mn)',desc:'Find the longest ordered subsequence shared by two sequences.',steps:['Create a DP table.','Extend matching characters.','Otherwise keep the best neighboring state.']},
{id:'knapsack',name:'0/1 Knapsack',kind:'algorithm',group:'Dynamic Programming',icon:'bi-backpack',best:'O(nW)',avg:'O(nW)',worst:'O(nW)',space:'O(W)',desc:'Maximize value under a capacity when each item is used at most once.',steps:['Create capacity states.','Process capacities backwards.','Choose between taking and skipping.']},
{id:'kmp',name:'KMP String Search',kind:'algorithm',group:'Strings',icon:'bi-fonts',best:'O(n+m)',avg:'O(n+m)',worst:'O(n+m)',space:'O(m)',desc:'Search text without rechecking matched characters.',steps:['Build the prefix table.','Advance on a match.','Fall back using the table on mismatch.']},
{id:'nqueens',name:'N-Queens Backtracking',kind:'algorithm',group:'Backtracking',icon:'bi-grid-3x3',best:'O(n!)',avg:'O(n!)',worst:'O(n!)',space:'O(n)',desc:'Place queens row by row while pruning attacked columns and diagonals.',steps:['Try a safe column.','Mark its column and diagonals.','Backtrack after exploring the choice.']},
{id:'sliding',name:'Sliding Window',kind:'algorithm',group:'Patterns',icon:'bi-layout-three-columns',best:'O(n)',avg:'O(n)',worst:'O(n)',space:'O(1)',desc:'Update a fixed-size range without recomputing every element.',steps:['Build the first window.','Remove the outgoing value.','Add the incoming value and update the answer.']}
);
const code={
bubble:{python:`def bubble_sort(a):
    for end in range(len(a)-1, 0, -1):
        swapped = False
        for i in range(end):
            if a[i] > a[i+1]:
                a[i], a[i+1] = a[i+1], a[i]
                swapped = True
        if not swapped:
            break
    return a`,cpp:`void bubbleSort(vector<int>& a) {
    for (int end=a.size()-1; end>0; --end) {
        bool swapped=false;
        for (int i=0; i<end; ++i)
            if (a[i] > a[i+1]) {
                swap(a[i],a[i+1]); swapped=true;
            }
        if (!swapped) break;
    }
}`,java:`static void bubbleSort(int[] a) {
    for (int end=a.length-1; end>0; end--) {
        boolean swapped=false;
        for (int i=0; i<end; i++)
            if (a[i] > a[i+1]) {
                int t=a[i]; a[i]=a[i+1]; a[i+1]=t; swapped=true;
            }
        if (!swapped) break;
    }
}`,ruby:`def bubble_sort(a)
  (a.length - 1).downto(1) do |last|
    swapped = false
    (0...last).each do |i|
      if a[i] > a[i + 1]
        a[i], a[i + 1] = a[i + 1], a[i]
        swapped = true
      end
    end
    break unless swapped
  end
  a
end`},
binary:{python:`def binary_search(a, target):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == target: return mid
        if a[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1`,cpp:`int binarySearch(const vector<int>& a,int x){int l=0,r=a.size()-1;while(l<=r){int m=l+(r-l)/2;if(a[m]==x)return m;if(a[m]<x)l=m+1;else r=m-1;}return -1;}`,java:`static int binarySearch(int[] a,int x){int l=0,r=a.length-1;while(l<=r){int m=l+(r-l)/2;if(a[m]==x)return m;if(a[m]<x)l=m+1;else r=m-1;}return -1;}`,ruby:`def binary_search(a, x)
  left, right = 0, a.length - 1
  while left <= right
    mid = (left + right) / 2
    return mid if a[mid] == x
    a[mid] < x ? left = mid + 1 : right = mid - 1
  end
  -1
end`},
stack:{python:`class Stack:
    def __init__(self): self.data = []
    def push(self, value): self.data.append(value)
    def pop(self):
        if not self.data: raise IndexError("empty stack")
        return self.data.pop()
    def peek(self): return self.data[-1] if self.data else None`,cpp:`class Stack{vector<int> a;public:void push(int x){a.push_back(x);}int pop(){if(a.empty())throw runtime_error("empty");int x=a.back();a.pop_back();return x;}int top()const{return a.back();}};`,java:`class IntStack { private final ArrayDeque<Integer> a=new ArrayDeque<>(); void push(int x){a.push(x);} int pop(){return a.pop();} int peek(){return a.peek();} }`,ruby:`class Stack
  def initialize = @data = []
  def push(value) = @data.push(value)
  def pop
    raise "empty stack" if @data.empty?
    @data.pop
  end
  def peek = @data.last
end`},
queue:{python:`from collections import deque
q = deque()
q.append(10)       # enqueue
front = q.popleft() # dequeue`,cpp:`queue<int> q; q.push(10); int front=q.front(); q.pop();`,java:`Queue<Integer> q=new ArrayDeque<>(); q.offer(10); int front=q.remove();`,ruby:`q = []; q << 10; front = q.shift`},
bfs:{python:`from collections import deque
def bfs(graph, start):
    seen={start}; q=deque([start]); order=[]
    while q:
        u=q.popleft(); order.append(u)
        for v in graph[u]:
            if v not in seen:
                seen.add(v); q.append(v)
    return order`,cpp:`vector<int> bfs(vector<vector<int>>& g,int s){queue<int>q;q.push(s);vector<int>seen(g.size()),out;seen[s]=1;while(!q.empty()){int u=q.front();q.pop();out.push_back(u);for(int v:g[u])if(!seen[v])seen[v]=1,q.push(v);}return out;}`,java:`static List<Integer> bfs(List<List<Integer>> g,int s){Queue<Integer>q=new ArrayDeque<>();boolean[] seen=new boolean[g.size()];List<Integer>out=new ArrayList<>();q.add(s);seen[s]=true;while(!q.isEmpty()){int u=q.remove();out.add(u);for(int v:g.get(u))if(!seen[v]){seen[v]=true;q.add(v);}}return out;}`,ruby:`def bfs(g, start)
  q=[start]; seen={start=>true}; order=[]
  until q.empty?
    u=q.shift; order << u
    g[u].each do |v|
      unless seen[v]
        seen[v] = true
        q << v
      end
    end
  end
  order
end`}
};
const generic={
python:t=>`# ${t.name} — runnable learning walkthrough\ndef ${t.id}_walkthrough(values):\n    steps = [\n        "${t.steps[0]}",\n        "${t.steps[1]}",\n        "${t.steps[2]}"\n    ]\n    return values, steps\n\nif __name__ == "__main__":\n    values = list(map(int, input("Enter integers: ").split()))\n    data, steps = ${t.id}_walkthrough(values)\n    print("Input:", *data)\n    for number, step in enumerate(steps, 1):\n        print(f"Step {number}: {step}")\n    print("Output: walkthrough completed")`,
cpp:t=>`#include <bits/stdc++.h>\nusing namespace std;\n\nvector<string> ${t.id}Walkthrough(const vector<int>& values) {\n    return {\n        "${t.steps[0]}",\n        "${t.steps[1]}",\n        "${t.steps[2]}"\n    };\n}\n\nint main() {\n    int n; cin >> n; vector<int> values(n);\n    for (int &value : values) cin >> value;\n    auto steps = ${t.id}Walkthrough(values);\n    cout << "Input:"; for (int value : values) cout << ' ' << value;\n    cout << '\\n';\n    for (int i=0; i<(int)steps.size(); ++i)\n        cout << "Step " << i+1 << ": " << steps[i] << '\\n';\n    cout << "Output: walkthrough completed\\n";\n}`,
java:t=>`import java.util.*;\n\npublic class Main {\n    static List<String> ${t.id}Walkthrough(int[] values) {\n        return List.of(\n            "${t.steps[0]}",\n            "${t.steps[1]}",\n            "${t.steps[2]}"\n        );\n    }\n\n    public static void main(String[] args) {\n        Scanner scanner = new Scanner(System.in);\n        int n = scanner.nextInt();\n        int[] values = new int[n];\n        for (int i=0; i<n; i++) values[i] = scanner.nextInt();\n        List<String> steps = ${t.id}Walkthrough(values);\n        System.out.println("Input: " + Arrays.toString(values));\n        for (int i=0; i<steps.size(); i++)\n            System.out.println("Step " + (i+1) + ": " + steps.get(i));\n        System.out.println("Output: walkthrough completed");\n    }\n}`,
ruby:t=>`# ${t.name} — runnable learning walkthrough\ndef ${t.id}_walkthrough(values)\n  [\n    "${t.steps[0]}",\n    "${t.steps[1]}",\n    "${t.steps[2]}"\n  ]\nend\n\nvalues = STDIN.read.split.map(&:to_i)\nsteps = ${t.id}_walkthrough(values)\nputs "Input: #{values.join(' ')}"\nsteps.each_with_index { |step, i| puts "Step #{i + 1}: #{step}" }\nputs "Output: walkthrough completed"`
};
Object.assign(code,{
selection:{python:`def selection_sort(a):
    for i in range(len(a)):
        minimum = i
        for j in range(i + 1, len(a)):
            if a[j] < a[minimum]: minimum = j
        a[i], a[minimum] = a[minimum], a[i]
    return a`,cpp:`void selectionSort(vector<int>& a){
    for(int i=0;i<(int)a.size();++i){
        int mn=i;
        for(int j=i+1;j<(int)a.size();++j) if(a[j]<a[mn]) mn=j;
        swap(a[i],a[mn]);
    }
}`,java:`static void selectionSort(int[] a){
    for(int i=0;i<a.length;i++){
        int min=i;
        for(int j=i+1;j<a.length;j++) if(a[j]<a[min]) min=j;
        int t=a[i]; a[i]=a[min]; a[min]=t;
    }
}`,ruby:`def selection_sort(a)
  a.each_index do |i|
    min = (i...a.length).min_by { |j| a[j] }
    a[i], a[min] = a[min], a[i]
  end
  a
end`},
insertion:{python:`def insertion_sort(a):
    for i in range(1, len(a)):
        key, j = a[i], i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]; j -= 1
        a[j + 1] = key
    return a`,cpp:`void insertionSort(vector<int>& a){
    for(int i=1;i<(int)a.size();++i){
        int key=a[i],j=i-1;
        while(j>=0&&a[j]>key){a[j+1]=a[j];--j;}
        a[j+1]=key;
    }
}`,java:`static void insertionSort(int[] a){
    for(int i=1;i<a.length;i++){
        int key=a[i],j=i-1;
        while(j>=0&&a[j]>key){a[j+1]=a[j--];}
        a[j+1]=key;
    }
}`,ruby:`def insertion_sort(a)
  (1...a.length).each do |i|
    key, j = a[i], i - 1
    while j >= 0 && a[j] > key
      a[j + 1] = a[j]; j -= 1
    end
    a[j + 1] = key
  end
  a
end`},
merge:{python:`def merge_sort(a):
    return a if len(a) < 2
    mid = len(a) // 2
    left, right = merge_sort(a[:mid]), merge_sort(a[mid:])
    out = []
    while left and right:
        out.append((left if left[0] <= right[0] else right).pop(0))
    return out + left + right`,cpp:`vector<int> mergeSort(vector<int> a){
    if(a.size()<2) return a;
    int m=a.size()/2;
    vector<int> l(a.begin(),a.begin()+m),r(a.begin()+m,a.end()),out;
    l=mergeSort(l); r=mergeSort(r);
    merge(l.begin(),l.end(),r.begin(),r.end(),back_inserter(out));
    return out;
}`,java:`static int[] mergeSort(int[] a){
    if(a.length<2) return a;
    int m=a.length/2;
    int[] l=mergeSort(Arrays.copyOfRange(a,0,m));
    int[] r=mergeSort(Arrays.copyOfRange(a,m,a.length));
    int[] out=new int[a.length]; int i=0,j=0,k=0;
    while(i<l.length||j<r.length) out[k++]=j==r.length||(i<l.length&&l[i]<=r[j])?l[i++]:r[j++];
    return out;
}`,ruby:`def merge_sort(a)
  return a if a.length < 2
  mid = a.length / 2
  left, right = merge_sort(a[...mid]), merge_sort(a[mid..])
  left.zip(right).flatten.compact.sort
end`},
quick:{python:`def quick_sort(a):
    if len(a) < 2: return a
    pivot = a[len(a) // 2]
    return quick_sort([x for x in a if x < pivot]) + \\
           [x for x in a if x == pivot] + \\
           quick_sort([x for x in a if x > pivot])`,cpp:`void quickSort(vector<int>& a,int lo,int hi){
    if(lo>=hi) return;
    int i=lo,j=hi,p=a[lo+(hi-lo)/2];
    while(i<=j){while(a[i]<p)i++;while(a[j]>p)j--;if(i<=j)swap(a[i++],a[j--]);}
    quickSort(a,lo,j); quickSort(a,i,hi);
}`,java:`static void quickSort(int[] a,int lo,int hi){
    if(lo>=hi)return;
    int i=lo,j=hi,p=a[lo+(hi-lo)/2];
    while(i<=j){while(a[i]<p)i++;while(a[j]>p)j--;if(i<=j){int t=a[i];a[i++]=a[j];a[j--]=t;}}
    quickSort(a,lo,j); quickSort(a,i,hi);
}`,ruby:`def quick_sort(a)
  return a if a.length < 2
  pivot = a[a.length / 2]
  quick_sort(a.select { |x| x < pivot }) +
    a.select { |x| x == pivot } +
    quick_sort(a.select { |x| x > pivot })
end`},
linear:{python:`def linear_search(a, target):
    for i, value in enumerate(a):
        return i if value == target
    return -1`,cpp:`int linearSearch(const vector<int>& a,int target){
    for(int i=0;i<(int)a.size();++i) if(a[i]==target) return i;
    return -1;
}`,java:`static int linearSearch(int[] a,int target){
    for(int i=0;i<a.length;i++) if(a[i]==target) return i;
    return -1;
}`,ruby:`def linear_search(a, target)
  a.each_with_index { |value, i| return i if value == target }
  -1
end`},
dfs:{python:`def dfs(graph, start):
    seen, order = set(), []
    def visit(u):
        seen.add(u); order.append(u)
        for v in graph[u]:
            if v not in seen: visit(v)
    visit(start)
    return order`,cpp:`void dfs(int u,const vector<vector<int>>& g,vector<int>& seen,vector<int>& out){
    seen[u]=1; out.push_back(u);
    for(int v:g[u]) if(!seen[v]) dfs(v,g,seen,out);
}`,java:`static void dfs(int u,List<List<Integer>> g,boolean[] seen,List<Integer> out){
    seen[u]=true; out.add(u);
    for(int v:g.get(u)) if(!seen[v]) dfs(v,g,seen,out);
}`,ruby:`def dfs(g, u, seen = {}, order = [])
  seen[u] = true; order << u
  g[u].each { |v| dfs(g, v, seen, order) unless seen[v] }
  order
end`},
counting:{python:`def counting_sort(a):
    if not a: return []
    count = [0] * (max(a) + 1)
    for x in a: count[x] += 1
    return [x for x, n in enumerate(count) for _ in range(n)]`,cpp:`vector<int> countingSort(const vector<int>& a){
    if(a.empty())return {};
    vector<int> c(*max_element(a.begin(),a.end())+1),out;
    for(int x:a)c[x]++;
    for(int x=0;x<(int)c.size();x++)while(c[x]--)out.push_back(x);
    return out;
}`,java:`static int[] countingSort(int[] a){
    int max=Arrays.stream(a).max().orElse(0),k=0; int[] c=new int[max+1],out=new int[a.length];
    for(int x:a)c[x]++;
    for(int x=0;x<c.length;x++)while(c[x]-->0)out[k++]=x;
    return out;
}`,ruby:`def counting_sort(a)
  counts = Array.new(a.max.to_i + 1, 0)
  a.each { |x| counts[x] += 1 }
  counts.each_index.flat_map { |x| [x] * counts[x] }
end`},
sliding:{python:`def max_window_sum(a, k):
    window = sum(a[:k]); best = window
    for i in range(k, len(a)):
        window += a[i] - a[i-k]
        best = max(best, window)
    return best`,cpp:`long long maxWindowSum(const vector<int>& a,int k){
    long long window=accumulate(a.begin(),a.begin()+k,0LL),best=window;
    for(int i=k;i<(int)a.size();++i){window+=a[i]-a[i-k];best=max(best,window);}
    return best;
}`,java:`static long maxWindowSum(int[] a,int k){
    long window=0; for(int i=0;i<k;i++)window+=a[i]; long best=window;
    for(int i=k;i<a.length;i++){window+=a[i]-a[i-k];best=Math.max(best,window);}
    return best;
}`,ruby:`def max_window_sum(a, k)
  window = a.first(k).sum
  best = window
  (k...a.length).each { |i| window += a[i] - a[i-k]; best = [best, window].max }
  best
end`}
});
Object.assign(code,{
array:{python:`values=list(map(int,input().split()))
values.append(99)
print("Array:",*values)
print("Index 0:",values[0])`,cpp:`#include <bits/stdc++.h>
using namespace std;int main(){int n,x;cin>>n;vector<int>a;while(n--){cin>>x;a.push_back(x);}a.push_back(99);cout<<"Array: ";for(int v:a)cout<<v<<' ';cout<<"\nIndex 0: "<<a[0];}`,java:`import java.util.*;public class Main{public static void main(String[]z){Scanner s=new Scanner(System.in);int n=s.nextInt();ArrayList<Integer>a=new ArrayList<>();while(n-->0)a.add(s.nextInt());a.add(99);System.out.println("Array: "+a);System.out.println("Index 0: "+a.get(0));}}`,ruby:`a=STDIN.read.split.map(&:to_i);a<<99;puts "Array: #{a.join(' ')}";puts "Index 0: #{a[0]}"`},
deque:{python:`from collections import deque
values=list(map(int,input().split()));d=deque(values)
d.appendleft(-1);d.append(99)
print("Deque:",*d)
print("Pop front:",d.popleft());print("Pop rear:",d.pop())`,cpp:`#include <bits/stdc++.h>
using namespace std;int main(){int n,x;cin>>n;deque<int>d;while(n--){cin>>x;d.push_back(x);}d.push_front(-1);d.push_back(99);cout<<"Deque: ";for(int v:d)cout<<v<<' ';cout<<"\nPop front: "<<d.front();d.pop_front();cout<<"\nPop rear: "<<d.back();}`,java:`import java.util.*;public class Main{public static void main(String[]z){Scanner s=new Scanner(System.in);Deque<Integer>d=new ArrayDeque<>();int n=s.nextInt();while(n-->0)d.addLast(s.nextInt());d.addFirst(-1);d.addLast(99);System.out.println("Deque: "+d);System.out.println("Pop front: "+d.removeFirst());System.out.println("Pop rear: "+d.removeLast());}}`,ruby:`d=STDIN.read.split.map(&:to_i);d.unshift(-1);d<<99;puts "Deque: #{d.join(' ')}";puts "Pop front: #{d.shift}";puts "Pop rear: #{d.pop}"`},
hash:{python:`values=list(map(int,input().split()))
freq={}
for value in values:freq[value]=freq.get(value,0)+1
for key in sorted(freq):print(key,"=>",freq[key])`,cpp:`#include <bits/stdc++.h>
using namespace std;int main(){int n,x;cin>>n;unordered_map<int,int>freq;while(n--){cin>>x;freq[x]++;}vector<pair<int,int>>out(freq.begin(),freq.end());sort(out.begin(),out.end());for(auto [k,v]:out)cout<<k<<" => "<<v<<'\n';}`,java:`import java.util.*;public class Main{public static void main(String[]z){Scanner s=new Scanner(System.in);int n=s.nextInt();Map<Integer,Integer>f=new TreeMap<>();while(n-->0){int x=s.nextInt();f.put(x,f.getOrDefault(x,0)+1);}f.forEach((k,v)->System.out.println(k+" => "+v));}}`,ruby:`freq=Hash.new(0);STDIN.read.split.map(&:to_i).each{|x|freq[x]+=1};freq.sort.each{|k,v|puts "#{k} => #{v}"}`},
heap:{python:`import heapq
values=list(map(int,input().split()));heapq.heapify(values)
print("Min heap:",values)
print("Removal order:",end=" ")
while values:print(heapq.heappop(values),end=" ")`,cpp:`#include <bits/stdc++.h>
using namespace std;int main(){int n,x;cin>>n;priority_queue<int,vector<int>,greater<int>>h;while(n--){cin>>x;h.push(x);}cout<<"Removal order: ";while(!h.empty()){cout<<h.top()<<' ';h.pop();}}`,java:`import java.util.*;public class Main{public static void main(String[]z){Scanner s=new Scanner(System.in);PriorityQueue<Integer>h=new PriorityQueue<>();int n=s.nextInt();while(n-->0)h.add(s.nextInt());System.out.print("Removal order: ");while(!h.isEmpty())System.out.print(h.remove()+" ");}}`,ruby:`h=STDIN.read.split.map(&:to_i);puts "Removal order: #{h.sort.join(' ')}"`},
linked:{python:`class Node:
    def __init__(self,value,next=None):self.value,self.next=value,next
values=list(map(int,input().split()));head=None
for value in reversed(values):head=Node(value,head)
print("Linked list:",end=" ")
while head:print(head.value,end=" -> ");head=head.next
print("NULL")`,cpp:`#include <bits/stdc++.h>
using namespace std;struct Node{int value;Node*next;Node(int v,Node*n=nullptr):value(v),next(n){}};int main(){int n,x;cin>>n;Node*head=nullptr,*tail=nullptr;while(n--){cin>>x;Node*node=new Node(x);if(!head)head=node;else tail->next=node;tail=node;}cout<<"Linked list: ";for(Node*p=head;p;p=p->next)cout<<p->value<<" -> ";cout<<"NULL";}`,java:`import java.util.*;class Node{int value;Node next;Node(int v){value=v;}}public class Main{public static void main(String[]z){Scanner s=new Scanner(System.in);int n=s.nextInt();Node head=null,tail=null;while(n-->0){Node node=new Node(s.nextInt());if(head==null)head=node;else tail.next=node;tail=node;}System.out.print("Linked list: ");for(Node p=head;p!=null;p=p.next)System.out.print(p.value+" -> ");System.out.println("NULL");}}`,ruby:`Node=Struct.new(:value,:next);head=nil;STDIN.read.split.map(&:to_i).reverse_each{|x|head=Node.new(x,head)};print "Linked list: ";while head;print "#{head.value} -> ";head=head.next;end;puts "NULL"`},
bst:{python:`class Node:
    def __init__(self,v):self.v,self.left,self.right=v,None,None
def insert(root,v):
    if root is None:return Node(v)
    if v<root.v:root.left=insert(root.left,v)
    else:root.right=insert(root.right,v)
    return root
def inorder(root):return inorder(root.left)+[root.v]+inorder(root.right) if root else []
root=None
for value in map(int,input().split()):root=insert(root,value)
print("Inorder:",*inorder(root))`,cpp:`#include <bits/stdc++.h>
using namespace std;struct Node{int v;Node*l=nullptr,*r=nullptr;Node(int x):v(x){}};Node*insert(Node*n,int x){if(!n)return new Node(x);if(x<n->v)n->l=insert(n->l,x);else n->r=insert(n->r,x);return n;}void inorder(Node*n){if(!n)return;inorder(n->l);cout<<n->v<<' ';inorder(n->r);}int main(){int n,x;cin>>n;Node*root=nullptr;while(n--){cin>>x;root=insert(root,x);}cout<<"Inorder: ";inorder(root);}`,java:`import java.util.*;class Node{int v;Node l,r;Node(int x){v=x;}}public class Main{static Node insert(Node n,int x){if(n==null)return new Node(x);if(x<n.v)n.l=insert(n.l,x);else n.r=insert(n.r,x);return n;}static void inorder(Node n){if(n==null)return;inorder(n.l);System.out.print(n.v+" ");inorder(n.r);}public static void main(String[]z){Scanner s=new Scanner(System.in);int n=s.nextInt();Node root=null;while(n-->0)root=insert(root,s.nextInt());System.out.print("Inorder: ");inorder(root);}}`,ruby:`Node=Struct.new(:v,:left,:right);def insert(n,x);return Node.new(x) unless n;x<n.v ? n.left=insert(n.left,x) : n.right=insert(n.right,x);n;end;def inorder(n);n ? inorder(n.left)+[n.v]+inorder(n.right) : [];end;root=nil;STDIN.read.split.map(&:to_i).each{|x|root=insert(root,x)};puts "Inorder: #{inorder(root).join(' ')}"`},
dijkstra:{python:`import heapq
graph=[[(1,4),(2,1)],[(3,1)],[(1,2),(3,5)],[]]
dist=[float('inf')]*4;dist[0]=0;pq=[(0,0)]
while pq:
    d,u=heapq.heappop(pq)
    if d!=dist[u]:continue
    for v,w in graph[u]:
        if d+w<dist[v]:dist[v]=d+w;heapq.heappush(pq,(dist[v],v))
print("Distances:",*dist)`,cpp:`#include <bits/stdc++.h>
using namespace std;int main(){vector<vector<pair<int,int>>>g={{{1,4},{2,1}},{{3,1}},{{1,2},{3,5}}, {}};vector<int>d(4,1e9);priority_queue<pair<int,int>,vector<pair<int,int>>,greater<pair<int,int>>>pq;d[0]=0;pq.push({0,0});while(!pq.empty()){auto[du,u]=pq.top();pq.pop();if(du!=d[u])continue;for(auto[v,w]:g[u])if(du+w<d[v]){d[v]=du+w;pq.push({d[v],v});}}cout<<"Distances: ";for(int x:d)cout<<x<<' ';}`,java:`import java.util.*;public class Main{public static void main(String[]z){int[][][]g={{{1,4},{2,1}},{{3,1}},{{1,2},{3,5}}, {}};int[]d={0,999999,999999,999999};PriorityQueue<int[]>q=new PriorityQueue<>(Comparator.comparingInt(a->a[0]));q.add(new int[]{0,0});while(!q.isEmpty()){int[]p=q.remove();if(p[0]!=d[p[1]])continue;for(int[]e:g[p[1]])if(p[0]+e[1]<d[e[0]]){d[e[0]]=p[0]+e[1];q.add(new int[]{d[e[0]],e[0]});}}System.out.println("Distances: "+Arrays.toString(d));}}`,ruby:`g=[[[1,4],[2,1]],[[3,1]],[[1,2],[3,5]],[]];d=[0,Float::INFINITY,Float::INFINITY,Float::INFINITY];q=[[0,0]];until q.empty?;q.sort!;du,u=q.shift;next if du!=d[u];g[u].each{|v,w|if du+w<d[v];d[v]=du+w;q<<[d[v],v];end};end;puts "Distances: #{d.join(' ')}"`}
});
let selected=topics[0],filter='all',values=[8,3,5,1,9,2],frames=[],index=0,timer=null,currentCode='',auxValue=5;
function sortFrames(arr,type){const a=[...arr],out=[{a:[...a],active:[],text:'Read the input array.',phase:'input'}];if(type==='selection'){for(let i=0;i<a.length;i++){let m=i;out.push({a:[...a],active:[i],done:i,text:`Start pass ${i+1}; current minimum index is ${i}.`,phase:'outer'});for(let j=i+1;j<a.length;j++){out.push({a:[...a],active:[m,j],done:i,text:`Compare current minimum ${a[m]} with ${a[j]}.`,phase:'compare'});if(a[j]<a[m]){m=j;out.push({a:[...a],active:[m],done:i,text:`${a[m]} is the new minimum.`,phase:'minimum'});}}[a[i],a[m]]=[a[m],a[i]];out.push({a:[...a],active:[i,m],done:i+1,text:`Swap and place ${a[i]} at index ${i}.`,phase:'swap'});}}else if(type==='insertion'){for(let i=1;i<a.length;i++){let j=i;out.push({a:[...a],active:[i],done:i,text:`Take ${a[i]} as the key.`,phase:'key'});while(j>0&&a[j-1]>a[j]){out.push({a:[...a],active:[j-1,j],done:i,text:'Compare key with the previous value.',phase:'compare'});[a[j-1],a[j]]=[a[j],a[j-1]];out.push({a:[...a],active:[j-1,j],done:i,text:'Shift the larger value right.',phase:'shift'});j--;}out.push({a:[...a],active:[j],done:i+1,text:'Insert the key into the sorted prefix.',phase:'insert'});}}else{for(let end=a.length-1;end>0;end--){out.push({a:[...a],active:[],done:a.length-1-end,text:`Begin pass; unsorted range ends at ${end}.`,phase:'outer'});let swapped=false;for(let i=0;i<end;i++){out.push({a:[...a],active:[i,i+1],text:`Compare ${a[i]} and ${a[i+1]}.`,phase:'compare'});if(a[i]>a[i+1]){[a[i],a[i+1]]=[a[i+1],a[i]];swapped=true;out.push({a:[...a],active:[i,i+1],text:'Swap the out-of-order pair.',phase:'swap'});}}if(!swapped){out.push({a:[...a],active:[],done:a.length,text:'No swap occurred, so the array is already sorted.',phase:'break'});break;}}}out.push({a:[...a],active:[],done:a.length,text:'Return the completely sorted array.',phase:'return'});return out}
function linearFrames(arr){const out=[{a:[...arr],active:[],text:`Start from index 0 and search for ${auxValue}.`,phase:'input'}];for(let i=0;i<arr.length;i++){out.push({a:[...arr],active:[i],done:i,text:`Compare a[${i}] = ${arr[i]} with target ${auxValue}.`,phase:'compare'});if(arr[i]===auxValue){out.push({a:[...arr],active:[i],done:i+1,text:`Target found at index ${i}.`,phase:'return'});return out}}out.push({a:[...arr],active:[],done:arr.length,text:'Target was not found; return -1.',phase:'return'});return out}
function binaryFrames(arr){const a=[...arr].sort((x,y)=>x-y),target=auxValue,out=[{a:[...a],active:[],text:`Sort the input and search for ${target}.`,phase:'input'}];let lo=0,hi=a.length-1;while(lo<=hi){const mid=Math.floor((lo+hi)/2);out.push({a:[...a],active:[mid],range:[lo,hi],text:`Check middle index ${mid}: ${a[mid]}.`,phase:'middle'});if(a[mid]===target){out.push({a:[...a],active:[mid],done:a.length,text:`Target found at index ${mid}.`,phase:'return'});return out}if(a[mid]<target){lo=mid+1;out.push({a:[...a],active:[mid],range:[lo,hi],text:'Discard the left half.',phase:'right'});}else{hi=mid-1;out.push({a:[...a],active:[mid],range:[lo,hi],text:'Discard the right half.',phase:'left'});}}out.push({a:[...a],active:[],text:'Target not found; return -1.',phase:'return'});return out}
function stackFrames(arr){const state=[],out=[{a:[],active:[],text:'Create an empty stack.',phase:'input'}];arr.forEach(v=>{state.push(v);out.push({a:[...state],active:[state.length-1],text:`Push ${v} onto the top.`,phase:'insert'});});for(let i=state.length-1;i>=0;i--){out.push({a:[...state],active:[state.length-1],text:`Top is ${state.at(-1)}; pop it.`,phase:'return'});state.pop();out.push({a:[...state],active:[],text:'Stack updated after pop.',phase:'loop'});}out.push({a:[],active:[],text:'Stack is empty.',phase:'return'});return out}
function queueFrames(arr){const state=[],out=[{a:[],active:[],text:'Create an empty queue.',phase:'input'}];arr.forEach(v=>{state.push(v);out.push({a:[...state],active:[state.length-1],text:`Enqueue ${v} at the rear.`,phase:'insert'});});while(state.length){out.push({a:[...state],active:[0],text:`Front is ${state[0]}; dequeue it.`,phase:'return'});state.shift();out.push({a:[...state],active:[],text:'Queue moved forward.',phase:'loop'});}out.push({a:[],active:[],text:'Queue is empty.',phase:'return'});return out}
function graphData(arr){const labels=Array.from({length:Math.min(7,arr.length)},(_,i)=>i),edges=[];for(let i=1;i<labels.length;i++)edges.push([Math.floor((i-1)/2),i]);return {labels,edges}}
function graphFrames(arr,type){const {labels,edges}=graphData(arr),adj=labels.map(()=>[]);edges.forEach(([a,b])=>{adj[a].push(b);adj[b].push(a)});const out=[{a:labels,edges,active:[0],visited:[],text:`Start ${type.toUpperCase()} from node ${labels[0]}.`,phase:'input'}],seen=new Set(),order=[];if(type==='bfs'){const q=[0];seen.add(0);while(q.length){const u=q.shift();order.push(u);out.push({a:labels,edges,active:[u],visited:[...order],text:`Visit ${labels[u]} and inspect its neighbors.`,phase:'loop'});for(const v of adj[u])if(!seen.has(v)){seen.add(v);q.push(v);out.push({a:labels,edges,active:[v],visited:[...order],queued:[...q],text:`Discover ${labels[v]} and enqueue it.`,phase:'insert'});}}}else{function visit(u){seen.add(u);order.push(u);out.push({a:labels,edges,active:[u],visited:[...order],text:`Visit ${labels[u]} and go deeper.`,phase:'loop'});for(const v of adj[u])if(!seen.has(v)){out.push({a:labels,edges,active:[u,v],visited:[...order],text:`Follow edge ${labels[u]} → ${labels[v]}.`,phase:'compare'});visit(v);}out.push({a:labels,edges,active:[u],visited:[...order],text:`Backtrack from ${labels[u]}.`,phase:'return'});}visit(0);}out.push({a:labels,edges,active:[],visited:[...order],text:`Traversal complete: ${order.map(i=>labels[i]).join(' → ')}`,phase:'return'});return out}
function slidingFrames(arr){const k=Math.min(3,arr.length),out=[];if(!k)return simpleFrames(arr);let sum=arr.slice(0,k).reduce((a,b)=>a+b,0),best=sum;out.push({a:[...arr],active:Array.from({length:k},(_,i)=>i),window:[0,k-1],text:`Build first window; sum = ${sum}.`,phase:'input'});for(let right=k;right<arr.length;right++){const left=right-k;sum+=arr[right]-arr[left];best=Math.max(best,sum);out.push({a:[...arr],active:Array.from({length:k},(_,i)=>left+1+i),window:[left+1,right],text:`Remove ${arr[left]}, add ${arr[right]}; window sum = ${sum}, best = ${best}.`,phase:'loop'});}out.push({a:[...arr],active:[],window:[],text:`Maximum window sum is ${best}.`,phase:'return'});return out}
function mergeFrames(arr){const a=[...arr],out=[{a:[...a],active:[],text:'Split the array recursively into single-element ranges.',phase:'input'}];function run(l,r){if(r-l<2)return;const m=Math.floor((l+r)/2);run(l,m);run(m,r);const merged=[];let i=l,j=m;out.push({a:[...a],active:[l,m],text:`Merge ranges [${l}, ${m-1}] and [${m}, ${r-1}].`,phase:'loop'});while(i<m&&j<r)merged.push(a[i]<=a[j]?a[i++]:a[j++]);while(i<m)merged.push(a[i++]);while(j<r)merged.push(a[j++]);for(let k=0;k<merged.length;k++){a[l+k]=merged[k];out.push({a:[...a],active:[l+k],text:`Write ${merged[k]} into index ${l+k}.`,phase:'insert'});}}run(0,a.length);out.push({a:[...a],active:[],done:a.length,text:'All merged ranges are sorted; return the result.',phase:'return'});return out}
function quickFrames(arr){const a=[...arr],out=[{a:[...a],active:[],text:'Use the input array for in-place partitioning.',phase:'input'}];function run(lo,hi){if(lo>=hi)return;let i=lo,j=hi,p=a[Math.floor((lo+hi)/2)];out.push({a:[...a],active:[Math.floor((lo+hi)/2)],text:`Choose pivot ${p}.`,phase:'key'});while(i<=j){while(a[i]<p)i++;while(a[j]>p)j--;if(i<=j){out.push({a:[...a],active:[i,j],text:`Swap ${a[i]} and ${a[j]} across the pivot.`,phase:'swap'});[a[i],a[j]]=[a[j],a[i]];out.push({a:[...a],active:[i,j],text:'Partition updated.',phase:'compare'});i++;j--;}}run(lo,j);run(i,hi);}run(0,a.length-1);out.push({a:[...a],active:[],done:a.length,text:'Every partition is sorted.',phase:'return'});return out}
function countingFrames(arr){const a=[...arr],out=[{a:[...a],active:[],text:'Create a frequency array up to the largest value.',phase:'input'}],count=Array(Math.max(...a,0)+1).fill(0);a.forEach((v,i)=>{count[v]++;out.push({a:[...a],active:[i],text:`Count value ${v}; frequency is now ${count[v]}.`,phase:'loop'});});let k=0;for(let v=0;v<count.length;v++)while(count[v]--){a[k]=v;out.push({a:[...a],active:[k],done:k+1,text:`Write ${v} at sorted index ${k}.`,phase:'insert'});k++;}out.push({a:[...a],active:[],done:a.length,text:'Return the rebuilt sorted array.',phase:'return'});return out}
function simpleFrames(arr){return [{a:[...arr],active:[],text:`Initialize ${selected.name}.`,phase:'input'},...arr.map((_,i)=>({a:[...arr],active:[i],done:i,text:`Process index ${i}: value ${arr[i]}.`,phase:'loop'})),{a:[...arr],active:[],done:arr.length,text:`${selected.name} operation complete.`,phase:'return'}]}
function buildFrames(){frames=['bubble','selection','insertion'].includes(selected.id)?sortFrames(values,selected.id):selected.id==='merge'?mergeFrames(values):selected.id==='quick'?quickFrames(values):selected.id==='counting'?countingFrames(values):selected.id==='linear'?linearFrames(values):selected.id==='binary'?binaryFrames(values):selected.id==='stack'?stackFrames(values):selected.id==='queue'?queueFrames(values):selected.id==='bfs'?graphFrames(values,'bfs'):selected.id==='dfs'?graphFrames(values,'dfs'):selected.id==='sliding'?slidingFrames(values):simpleFrames(values);index=0;renderFrame()}
function traceLine(frame){const lines=currentCode.split('\n'),phase=frame.phase||'',phaseKeys={input:['input(','cin>>','scanner','gets','readline'],outer:['for i','for(int i','for (int i','each_index','downto'],compare:['if a[','if(a[','if (a[','if value','return i if'],minimum:['minimum = j','mn=j','min=j'],swap:['swap(','a[i], a[','int t=a[i]'],break:['if not swapped','if (!swapped)','unless swapped'],key:['key, j','key=a[i]','key = a[i]'],shift:['while j','while(j','while (j'],insert:['a[j + 1] = key','a[j+1]=key'],middle:['mid =','int m=','mid = ('],right:['lo = mid','l=m+1','left = mid'],left:['hi = mid','r=m-1','right = mid'],loop:['for ','while ','each'],return:['return ','puts ','cout<<','system.out']};let keys=phaseKeys[phase]||[];const q=(frame.text||'').toLowerCase();if(!keys.length)keys=q.includes('swap')?phaseKeys.swap:q.includes('compare')?phaseKeys.compare:phaseKeys.loop;let found=-1;for(const key of keys){found=lines.findIndex(line=>line.toLowerCase().includes(key.toLowerCase()));if(found>=0)break}return found<0?Math.min(1,lines.length-1):found}
function explainLine(line){const s=line.trim();if(!s)return 'Blank line separates logical parts of the implementation.';if(/^(#|\/\/)/.test(s))return 'This comment describes the purpose of the next operation.';if(/\b(for|each)\b/.test(s))return 'This loop visits the required elements or neighbors.';if(/\bwhile\b/.test(s))return 'The loop continues while the algorithm condition remains true.';if(/\bif\b/.test(s))return 'This condition decides which operation or branch is valid.';if(/return\b/.test(s))return 'This returns the completed result to the caller.';if(/swap|a\[.*\],/.test(s))return 'This line swaps the selected values in the data set.';if(/append|push|offer|add\(/.test(s))return 'This line adds the current value to the working data structure.';if(/pop|remove|popleft|shift/.test(s))return 'This line removes the next value according to the structure rules.';if(/dist|distance/.test(s))return 'This line reads or updates a shortest-path distance.';return 'This highlighted statement performs the operation currently represented by the visualizer.'}
function highlightCode(n){document.querySelectorAll('.avs-code-line').forEach((el,i)=>el.classList.toggle('active',i===n));const lines=currentCode.split('\n');$('avsActiveLine').textContent=`Line ${n+1}`;$('avsLineMeaning').textContent=explainLine(lines[n]||'');const active=document.querySelector('.avs-code-line.active');if(active)active.scrollIntoView({block:'nearest'})}
function visualMarkup(f){const active=i=>f.active.includes(i)?' active':'',done=i=>i<(f.done||0)?' done':'';if(selected.id==='stack')return `<div class="avs-stack-view">${f.a.map((v,i)=>`<div class="avs-stack-item${active(i)}">${v}${i===f.a.length-1?'<small>TOP</small>':''}</div>`).reverse().join('')}</div>`;if(['queue','deque','linked'].includes(selected.id))return `<div class="avs-flow-view"><b>FRONT</b>${f.a.map((v,i)=>`<div class="avs-flow-node${active(i)}">${v}</div>${i<f.a.length-1?'<i class="bi bi-arrow-right"></i>':''}`).join('')}<b>REAR</b></div>`;if(['bst','heap','trie'].includes(selected.id))return `<div class="avs-tree-view">${f.a.map((v,i)=>`<div class="avs-tree-node${active(i)}" style="--level:${Math.floor(Math.log2(i+1))}">${v}<small>${i?'NODE':'ROOT'}</small></div>`).join('')}</div>`;if(['bfs','dfs','dijkstra','bellman','kruskal','unionfind'].includes(selected.id)){const pos=[[50,12],[27,39],[73,39],[14,75],[39,75],[61,75],[86,75]],edges=f.edges||graphData(f.a).edges,visited=new Set(f.visited||[]);return `<div class="avs-graph-view"><svg viewBox="0 0 100 100" preserveAspectRatio="none">${edges.map(([a,b])=>`<line x1="${pos[a][0]}" y1="${pos[a][1]}" x2="${pos[b][0]}" y2="${pos[b][1]}" class="${visited.has(a)&&visited.has(b)?'visited':''}"/>`).join('')}</svg>${f.a.map((v,i)=>`<div class="avs-graph-node${active(i)}${visited.has(i)?' visited':''}" style="left:${pos[i][0]}%;top:${pos[i][1]}%"><small>${i}</small>${v}</div>`).join('')}<div class="avs-graph-legend"><span>● Current</span><span>● Visited</span></div></div>`}if(['dp','lcs','knapsack','nqueens','kmp'].includes(selected.id))return `<div class="avs-grid-view">${f.a.map((v,i)=>`<div class="avs-grid-cell${active(i)}${done(i)}"><small>${i}</small>${v}</div>`).join('')}</div>`;return f.a.map((v,i)=>`<div class="${selected.kind==='structure'?'avs-node':'avs-bar'}${active(i)}${done(i)}" style="--v:${Math.max(1,Math.min(10,Math.abs(v)))}"><span>${v}</span></div>`).join('')}
function renderFrame(){const f=frames[index]||{a:values,active:[]};$('avsCanvas').className=`avs-canvas visual-${selected.id}`;$('avsCanvas').innerHTML=visualMarkup(f);$('avsNarration').querySelector('span').textContent=f.text;$('avsStepCount').textContent=`Step ${index+1} / ${frames.length}`;highlightCode(traceLine(f))}
function renderTopics(){const q=$('avsSearch').value.toLowerCase();$('avsTopicList').innerHTML=topics.filter(t=>(filter==='all'||t.kind===filter)&&t.name.toLowerCase().includes(q)).map(t=>`<button class="avs-topic-item ${t.id===selected.id?'active':''}" data-id="${t.id}"><i class="bi ${t.icon}"></i><span>${t.name}</span><small>${t.group}</small></button>`).join('');document.querySelectorAll('.avs-topic-item').forEach(b=>b.onclick=()=>selectTopic(b.dataset.id))}
function selectTopic(id){selected=topics.find(t=>t.id===id)||topics[0];$('avsCategory').textContent=(selected.kind==='structure'?'DATA STRUCTURE':'ALGORITHM')+' · '+selected.group.toUpperCase();$('avsTitle').textContent=selected.name;$('avsDescription').textContent=selected.desc;$('avsBest').textContent=selected.best;$('avsAverage').textContent=selected.avg;$('avsWorst').textContent=selected.worst;$('avsSpace').textContent=selected.space;$('avsExplanation').innerHTML=selected.steps.map(x=>`<li>${x}</li>`).join('');renderTopics();renderCode();buildFrames()}
function structureProgram(raw,lang){const id=selected.id;if(!['stack','queue','bfs','dfs','sliding'].includes(id))return null;if(id==='queue'){const q={python:`from collections import deque\nvalues=list(map(int,input().split()));q=deque(values)\nprint("Front:",q[0]);print("Dequeue:",end=" ")\nwhile q:print(q.popleft(),end=" ")`,cpp:`#include <bits/stdc++.h>\nusing namespace std;int main(){int n,x;cin>>n;queue<int>q;while(n--){cin>>x;q.push(x);}cout<<"Front: "<<q.front()<<"\\nDequeue: ";while(!q.empty()){cout<<q.front()<<' ';q.pop();}}`,java:`import java.util.*;public class Main{public static void main(String[]z){Scanner s=new Scanner(System.in);Queue<Integer>q=new ArrayDeque<>();int n=s.nextInt();while(n-->0)q.offer(s.nextInt());System.out.println("Front: "+q.peek());System.out.print("Dequeue: ");while(!q.isEmpty())System.out.print(q.remove()+" ");}}`,ruby:`q=STDIN.read.split.map(&:to_i);puts "Front: #{q.first}";print "Dequeue: ";print "#{q.shift} " until q.empty?`};return q[lang]}if(id==='stack'){if(lang==='python')return `${raw}\nvalues=list(map(int,input().split()));s=Stack()\nfor x in values:s.push(x)\nprint("Top:",s.peek());print("Pop:",end=" ")\nwhile s.data:print(s.pop(),end=" ")`;if(lang==='cpp')return `#include <bits/stdc++.h>\nusing namespace std;\n${raw}\nint main(){int n,x;cin>>n;Stack s;while(n--){cin>>x;s.push(x);}cout<<"Top: "<<s.top()<<"\\nPop: ";try{while(true)cout<<s.pop()<<' ';}catch(...){}}`;if(lang==='java')return `import java.util.*;${raw}public class Main{public static void main(String[]z){Scanner s=new Scanner(System.in);IntStack st=new IntStack();int n=s.nextInt();while(n-->0)st.push(s.nextInt());System.out.println("Top: "+st.peek());System.out.print("Pop: ");while(true)try{System.out.print(st.pop()+" ");}catch(Exception e){break;}}}`;return `${raw}\nv=STDIN.read.split.map(&:to_i);s=Stack.new;v.each{|x|s.push(x)};puts "Top: #{s.peek}";print "Pop: ";print "#{s.pop} " until s.instance_variable_get(:@data).empty?`}
if(id==='sliding'){if(lang==='python')return `${raw}\na=list(map(int,input().split()));k=int(input());print("Maximum window sum:",max_window_sum(a,k))`;if(lang==='cpp')return `#include <bits/stdc++.h>\nusing namespace std;\n${raw}\nint main(){int n,k;cin>>n>>k;vector<int>a(n);for(int&x:a)cin>>x;cout<<"Maximum window sum: "<<maxWindowSum(a,k);}`;if(lang==='java')return `import java.util.*;public class Main{${raw}public static void main(String[]z){Scanner s=new Scanner(System.in);int n=s.nextInt(),k=s.nextInt();int[]a=new int[n];for(int i=0;i<n;i++)a[i]=s.nextInt();System.out.println("Maximum window sum: "+maxWindowSum(a,k));}}`;return `${raw}\na=gets.split.map(&:to_i);k=gets.to_i;puts "Maximum window sum: #{max_window_sum(a,k)}"`}
const graph='[[1,2],[0,3,4],[0,5,6],[1],[1],[2],[2]]';if(lang==='python')return `${raw}\ngraph=${graph}\nprint("${id.toUpperCase()} order:",*${id}(graph,0))`;if(lang==='cpp')return `#include <bits/stdc++.h>\nusing namespace std;\n${raw}\nint main(){vector<vector<int>>g={{1,2},{0,3,4},{0,5,6},{1},{1},{2},{2}};${id==='bfs'?'auto out=bfs(g,0);':'vector<int>seen(7),out;dfs(0,g,seen,out);'}for(int x:out)cout<<x<<' ';}`;if(lang==='java')return `import java.util.*;public class Main{${raw}public static void main(String[]z){List<List<Integer>>g=List.of(List.of(1,2),List.of(0,3,4),List.of(0,5,6),List.of(1),List.of(1),List.of(2),List.of(2));${id==='bfs'?'List<Integer>out=bfs(g,0);':'boolean[]seen=new boolean[7];List<Integer>out=new ArrayList<>();dfs(0,g,seen,out);'}System.out.println("${id.toUpperCase()} order: "+out);}}`;return `${raw}\ng=${graph};puts "${id.toUpperCase()} order: #{${id}(g,0).join(' ')}"`}
function searchProgram(raw,lang){if(!['linear','binary'].includes(selected.id))return null;const fn=selected.id==='linear'?['linear_search','linearSearch']:['binary_search','binarySearch'];if(lang==='python')return `${raw}\n\nif __name__ == "__main__":\n    values = list(map(int, input("Enter integers: ").split()))\n    target = int(input("Target: "))\n    ${selected.id==='binary'?'values.sort()\n    ':''}index = ${fn[0]}(values, target)\n    print("Index:", index)`;if(lang==='cpp')return `#include <bits/stdc++.h>\nusing namespace std;\n\n${raw}\n\nint main(){\n    int n,target; cin>>n; vector<int> values(n);\n    for(int &x:values) cin>>x; cin>>target;\n    ${selected.id==='binary'?'sort(values.begin(),values.end());\n    ':''}cout << "Index: " << ${fn[1]}(values,target) << '\\n';\n    return 0;\n}`;if(lang==='java')return `import java.util.*;\npublic class Main {\n${raw.split('\n').map(x=>'    '+x).join('\n')}\n    public static void main(String[] args){\n        Scanner sc=new Scanner(System.in); int n=sc.nextInt();\n        int[] values=new int[n]; for(int i=0;i<n;i++)values[i]=sc.nextInt();\n        int target=sc.nextInt(); ${selected.id==='binary'?'Arrays.sort(values); ':''}\n        System.out.println("Index: " + ${fn[1]}(values,target));\n    }\n}`;return `${raw}\n\nvalues = gets.split.map(&:to_i)\ntarget = gets.to_i\n${selected.id==='binary'?'values.sort!\n':''}puts "Index: #{${fn[0]}(values, target)}"`}
function fullProgram(raw,lang){const search=searchProgram(raw,lang);if(search)return search;const sortCalls={bubble:['bubble_sort(values)','bubbleSort(values)','bubbleSort(values)','bubble_sort(values)'],selection:['selection_sort(values)','selectionSort(values)','selectionSort(values)','selection_sort(values)'],insertion:['insertion_sort(values)','insertionSort(values)','insertionSort(values)','insertion_sort(values)'],merge:['merge_sort(values)','values = mergeSort(values)','values = mergeSort(values)','merge_sort(values)'],quick:['quick_sort(values)','quickSort(values, 0, n - 1)','quickSort(values, 0, n - 1)','quick_sort(values)'],counting:['counting_sort(values)','values = countingSort(values)','values = countingSort(values)','counting_sort(values)']};const call=sortCalls[selected.id];if(!call)return raw;if(lang==='python')return `${raw}\n\nif __name__ == "__main__":\n    values = list(map(int, input("Enter integers: ").split()))\n    result = ${call[0]}\n    print("Sorted:", *result)`;if(lang==='cpp')return `#include <bits/stdc++.h>\nusing namespace std;\n\n${raw}\n\nint main(){\n    int n; cin >> n;\n    vector<int> values(n);\n    for(int &x: values) cin >> x;\n    ${call[1]};\n    for(int x: values) cout << x << ' ';\n    cout << '\\n';\n    return 0;\n}`;if(lang==='java')return `import java.util.*;\n\npublic class Main {\n${raw.split('\n').map(x=>'    '+x).join('\n')}\n\n    public static void main(String[] args) {\n        Scanner scanner = new Scanner(System.in);\n        int n = scanner.nextInt();\n        int[] values = new int[n];\n        for (int i = 0; i < n; i++) values[i] = scanner.nextInt();\n        ${call[2]};\n        System.out.println(Arrays.toString(values));\n    }\n}`;return `${raw}\n\nvalues = STDIN.read.split.map(&:to_i)\nresult = ${call[3]}\nputs "Sorted: #{result.join(' ')}"`}
function formatBracedCode(source){let out='',indent=0,paren=0,quote='',escaped=false;const pad=()=> '    '.repeat(Math.max(0,indent));const trimEnd=()=>{out=out.replace(/[ \t]+$/,'')};const newline=()=>{trimEnd();if(!out.endsWith('\n'))out+='\n';out+=pad()};for(let i=0;i<source.length;i++){const ch=source[i],next=source[i+1]||'';if(quote){out+=ch;if(escaped)escaped=false;else if(ch==='\\')escaped=true;else if(ch===quote)quote='';continue}if(ch==='"'||ch==="'"){quote=ch;out+=ch;continue}if(ch==='/'&&next==='/'){const end=source.indexOf('\n',i);out+=source.slice(i,end<0?source.length:end);i=(end<0?source.length:end)-1;newline();continue}if(ch==='('||ch==='[')paren++;if(ch===')'||ch===']')paren=Math.max(0,paren-1);if(ch==='{'){trimEnd();out+=' {';indent++;newline();continue}if(ch==='}'){indent=Math.max(0,indent-1);trimEnd();out=out.replace(/\n[ \t]*$/,'\n')+pad()+'}';if(next!==';'&&next!==','&&next!==')')newline();continue}if(ch===';'&&paren===0){out+=';';newline();continue}if(ch==='\n'){newline();continue}if(/\s/.test(ch)){if(out&&!/[\s]$/.test(out))out+=' ';continue}out+=ch}return out.replace(/[ \t]+\n/g,'\n').replace(/\n{3,}/g,'\n\n').trim()}
function formatPythonCode(source){const output=[];for(const original of source.split('\n')){const leading=(original.match(/^\s*/)||[''])[0],line=original.trim();if(!line){output.push('');continue}let quote='',escaped=false,paren=0,parts=[],start=0;for(let i=0;i<line.length;i++){const ch=line[i];if(quote){if(escaped)escaped=false;else if(ch==='\\')escaped=true;else if(ch===quote)quote='';continue}if(ch==='"'||ch==="'"){quote=ch;continue}if(ch==='('||ch==='['||ch==='{')paren++;else if(ch===')'||ch===']'||ch==='}')paren--;else if(ch===';'&&paren===0){parts.push(line.slice(start,i).trim());start=i+1}}parts.push(line.slice(start).trim());const first=parts.shift();const inline=first.match(/^((?:async\s+)?(?:def|class|if|elif|else|for|while|try|except|finally|with)\b.*?:)(.+)$/);if(inline){output.push(leading+inline[1]);output.push(leading+'    '+inline[2].trim())}else output.push(leading+first);parts.filter(Boolean).forEach(part=>output.push(leading+(/^(def|class|if|elif|else|for|while|try|except|finally|with)\b/.test(first)?'    ':'')+part))}return output.join('\n').replace(/\n{3,}/g,'\n\n').trim()}
function formatImplementation(source,lang){if(lang==='cpp'||lang==='java')return formatBracedCode(source);if(lang==='python')return formatPythonCode(source);return source.replace(/;/g,';\n').replace(/\n{3,}/g,'\n\n').trim()}
function renderCode(){const lang=$('avsLanguage').value,complete=Boolean(code[selected.id]&&code[selected.id][lang]);const raw=complete?code[selected.id][lang]:generic[lang](selected);currentCode=formatImplementation(complete?fullProgram(raw,lang):raw,lang);$('avsCode').innerHTML=currentCode.split('\n').map((line,i)=>`<span class="avs-code-line" data-line="${i+1}">${line.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</span>`).join('');$('avsLanguageLabel').textContent=({cpp:'C++',python:'Python',java:'Java',ruby:'Ruby'})[lang]+(complete?' · Complete runnable program':' · Guided operation walkthrough');highlightCode(0)}
function parseValues(){const a=$('avsInput').value.split(/[ ,]+/).map(Number).filter(Number.isFinite).slice(0,14);if(a.length)values=a;buildFrames()}
function stop(){clearInterval(timer);timer=null;$('avsPlay').innerHTML='<i class="bi bi-play-fill"></i><span>Play</span>'}
function programOutput(){const sorted=[...values].sort((a,b)=>a-b);if(['bubble','selection','insertion','merge','quick','counting','heapsort'].includes(selected.id))return `Input : ${values.join(' ')}\nSorted: ${sorted.join(' ')}\n\nProcess finished successfully.`;if(selected.id==='linear'){const target=values[values.length-1],position=values.indexOf(target);return `Array : ${values.join(' ')}\nTarget: ${target}\nIndex : ${position}\n\nProcess finished successfully.`}if(selected.id==='binary'){const target=sorted[Math.floor(sorted.length/2)],position=sorted.indexOf(target);return `Sorted array: ${sorted.join(' ')}\nTarget      : ${target}\nIndex       : ${position}\n\nProcess finished successfully.`}if(selected.id==='stack')return `Push: ${values.join(', ')}\nTop : ${values.at(-1)}\nPop : ${[...values].reverse().join(', ')}\n\nProcess finished successfully.`;if(selected.id==='queue'||selected.id==='deque')return `Enqueue: ${values.join(', ')}\nDequeue: ${values.join(', ')}\n\nProcess finished successfully.`;if(['bfs','dfs'].includes(selected.id))return `Start node: ${values[0]}\nTraversal : ${values.join(' → ')}\n\nProcess finished successfully.`;if(selected.id==='dp')return `States: ${values.map((_,i)=>i).join(' ')}\nResult: ${values.reduce((a,b)=>a+b,0)}\n\nProcess finished successfully.`;return `${selected.name}\nInput: ${values.join(' ')}\nCompleted ${frames.length} visual steps.\n\nProcess finished successfully.`}
function playAnimation(showOutput=false){stop();index=0;renderFrame();if(showOutput)$('avsOutput').textContent='Running visualization...';$('avsPlay').innerHTML='<i class="bi bi-pause-fill"></i><span>Pause</span>';timer=setInterval(()=>{if(index>=frames.length-1){stop();if(showOutput)$('avsOutput').textContent=programOutput();return}index++;renderFrame()},Math.max(120,1500-+$('avsSpeed').value))}
$('avsPlay').onclick=()=>{if(timer){stop();return}playAnimation(false)};
$('avsNext').onclick=()=>{stop();index=Math.min(frames.length-1,index+1);renderFrame()};$('avsPrev').onclick=()=>{stop();index=Math.max(0,index-1);renderFrame()};$('avsReset').onclick=()=>{stop();index=0;renderFrame()};$('avsApply').onclick=parseValues;$('avsRandom').onclick=()=>{$('avsInput').value=Array.from({length:7},()=>1+Math.floor(Math.random()*9)).join(', ');parseValues()};$('avsLanguage').onchange=renderCode;$('avsSearch').oninput=renderTopics;document.querySelectorAll('.avs-tabs button').forEach(b=>b.onclick=()=>{document.querySelectorAll('.avs-tabs button').forEach(x=>x.classList.remove('active'));b.classList.add('active');filter=b.dataset.kind;renderTopics()});$('avsCopy').onclick=async()=>{await navigator.clipboard.writeText($('avsCode').textContent);$('avsCopy').innerHTML='<i class="bi bi-check2"></i> Copied';setTimeout(()=>$('avsCopy').innerHTML='<i class="bi bi-copy"></i> Copy',1200)};
$('avsRun').onclick=()=>{parseValues();playAnimation(true)};$('avsClearOutput').onclick=()=>{$('avsOutput').textContent='Output cleared.'};
const baseFullProgram=fullProgram;
fullProgram=(raw,lang)=>structureProgram(raw,lang)||baseFullProgram(raw,lang);
const baseProgramOutput=programOutput;
programOutput=()=>{if(selected.id==='bfs')return `BFS order: ${values.slice(0,7).join(' → ')}\n\nProcess finished successfully.`;if(selected.id==='dfs'){const a=values.slice(0,7),order=[0,1,3,4,2,5,6].filter(i=>i<a.length).map(i=>a[i]);return `DFS order: ${order.join(' → ')}\n\nProcess finished successfully.`}if(selected.id==='sliding'){const k=Math.min(3,values.length);let best=-Infinity;for(let i=0;i+k<=values.length;i++)best=Math.max(best,values.slice(i,i+k).reduce((a,b)=>a+b,0));return `Array      : ${values.join(' ')}\nWindow size: ${k}\nMaximum sum: ${best}\n\nProcess finished successfully.`}return baseProgramOutput()};
const topicProgramOutput=programOutput;
programOutput=()=>{const n=Math.min(7,values.length);if(selected.id==='bfs')return `BFS order: ${Array.from({length:n},(_,i)=>i).join(' → ')}\n\nProcess finished successfully.`;if(selected.id==='dfs')return `DFS order: ${[0,1,3,4,2,5,6].filter(i=>i<n).join(' → ')}\n\nProcess finished successfully.`;return topicProgramOutput()};
const coreTopicIds=new Set(['bubble','selection','insertion','merge','quick','counting','linear','binary','array','linked','stack','queue','deque','hash','bst','heap','bfs','dfs','dijkstra','sliding']);
renderTopics=()=>{const query=$('avsSearch').value.toLowerCase(),filtered=topics.filter(t=>coreTopicIds.has(t.id)&&(filter==='all'||t.kind===filter)&&t.name.toLowerCase().includes(query)),groups=new Map();filtered.forEach(t=>{if(!groups.has(t.group))groups.set(t.group,[]);groups.get(t.group).push(t)});$('avsTopicList').innerHTML=[...groups].map(([group,list])=>`<section class="avs-topic-group"><h3>${group}</h3>${list.map(t=>`<button class="avs-topic-item ${t.id===selected.id?'active':''}" data-id="${t.id}"><i class="bi ${t.icon}"></i><span>${t.name}</span><small>${t.kind==='structure'?'DS':'ALG'}</small></button>`).join('')}</section>`).join('');document.querySelectorAll('.avs-topic-item').forEach(button=>button.onclick=()=>selectTopic(button.dataset.id))};
slidingFrames=(arr)=>{const k=Math.max(1,Math.min(Math.trunc(auxValue)||3,arr.length)),out=[];let sum=arr.slice(0,k).reduce((a,b)=>a+b,0),best=sum;out.push({a:[...arr],active:Array.from({length:k},(_,i)=>i),text:`Build window [0, ${k-1}]; sum = ${sum}.`,phase:'input'});for(let right=k;right<arr.length;right++){const left=right-k;sum+=arr[right]-arr[left];best=Math.max(best,sum);out.push({a:[...arr],active:Array.from({length:k},(_,i)=>left+1+i),text:`Remove ${arr[left]}, add ${arr[right]}; sum = ${sum}, best = ${best}.`,phase:'loop'});}out.push({a:[...arr],active:[],text:`Maximum window sum is ${best}.`,phase:'return'});return out};
const baseParseValues=parseValues;
parseValues=()=>{const aux=Number($('avsAuxInput').value);if(Number.isFinite(aux))auxValue=aux;baseParseValues()};
const baseSelectTopic=selectTopic;
selectTopic=(id)=>{baseSelectTopic(id);const aux=$('avsAuxInput'),hint=$('avsInputHint');if(['linear','binary'].includes(selected.id)){aux.hidden=false;aux.value=auxValue;aux.placeholder='Target';hint.textContent='Enter array values and the target to search.'}else if(selected.id==='sliding'){aux.hidden=false;aux.value=Math.max(1,Math.trunc(auxValue)||3);aux.placeholder='Window size';hint.textContent='Enter array values and window size (k).'}else{aux.hidden=true;hint.textContent=['bfs','dfs','dijkstra'].includes(selected.id)?'Graph topology is shown with numbered nodes and edges.':'Enter comma or space separated integers.'}buildFrames()};
const inputAwareBaseOutput=programOutput;
programOutput=()=>{if(selected.id==='linear')return `Array : ${values.join(' ')}\nTarget: ${auxValue}\nIndex : ${values.indexOf(auxValue)}\n\nProcess finished successfully.`;if(selected.id==='binary'){const sorted=[...values].sort((a,b)=>a-b);return `Sorted array: ${sorted.join(' ')}\nTarget      : ${auxValue}\nIndex       : ${sorted.indexOf(auxValue)}\n\nProcess finished successfully.`}if(selected.id==='sliding'){const k=Math.max(1,Math.min(Math.trunc(auxValue)||3,values.length));let best=-Infinity;for(let i=0;i+k<=values.length;i++)best=Math.max(best,values.slice(i,i+k).reduce((a,b)=>a+b,0));return `Array      : ${values.join(' ')}\nWindow size: ${k}\nMaximum sum: ${best}\n\nProcess finished successfully.`}return inputAwareBaseOutput()};
function arrayFrames(arr){const out=[{a:[...arr],active:[],text:'Allocate contiguous indexed storage.',phase:'input'}];arr.forEach((v,i)=>out.push({a:[...arr],active:[i],done:i,text:`Read index ${i} in O(1): value ${v}.`,phase:'loop'}));out.push({a:[...arr,99],active:[arr.length],done:arr.length,text:'Append 99 at the next available index.',phase:'insert'});return out}
function linkedFrames(arr){const out=[{a:[],active:[],text:'Start with HEAD = NULL.',phase:'input'}],list=[];arr.forEach(v=>{list.push(v);out.push({a:[...list],active:[list.length-1],text:`Create node ${v} and connect the previous node to it.`,phase:'insert'});});arr.forEach((v,i)=>out.push({a:[...arr],active:[i],done:i,text:`Follow next pointer and visit ${v}.`,phase:'loop'}));out.push({a:[...arr],active:[],done:arr.length,text:'The last next pointer reaches NULL.',phase:'return'});return out}
function dequeFrames(arr){const state=[],out=[{a:[],active:[],text:'Create an empty double-ended queue.',phase:'input'}];arr.forEach((v,i)=>{i%2?state.unshift(v):state.push(v);out.push({a:[...state],active:[i%2?0:state.length-1],text:`Push ${v} at the ${i%2?'front':'rear'}.`,phase:'insert'});});if(state.length){out.push({a:[...state],active:[0],text:`Pop front value ${state[0]}.`,phase:'return'});state.shift()}if(state.length){out.push({a:[...state],active:[state.length-1],text:`Pop rear value ${state.at(-1)}.`,phase:'return'});state.pop()}out.push({a:[...state],active:[],text:'Both ends were updated in O(1).',phase:'return'});return out}
function hashFrames(arr){const buckets=Array(7).fill(null).map(()=>[]),out=[{a:Array(7).fill('—'),active:[],text:'Create seven empty hash buckets.',phase:'input',buckets:buckets.map(x=>[...x])}];arr.forEach(v=>{const i=((v%7)+7)%7;buckets[i].push(v);out.push({a:buckets.map(x=>x.join(' · ')||'—'),active:[i],text:`hash(${v}) = ${i}; insert into bucket ${i}.`,phase:'insert',buckets:buckets.map(x=>[...x])});});out.push({a:buckets.map(x=>x.join(' · ')||'—'),active:[],done:7,text:'All keys are stored; chained values show collisions.',phase:'return',buckets});return out}
function treeInsertFrames(arr,type){const heap=[],out=[{a:[],active:[],text:`Create an empty ${type==='heap'?'min heap':'binary search tree'}.`,phase:'input'}];if(type==='heap'){arr.forEach(v=>{heap.push(v);let i=heap.length-1;out.push({a:[...heap],active:[i],text:`Insert ${v} at the next complete-tree position.`,phase:'insert'});while(i>0){const p=Math.floor((i-1)/2);if(heap[p]<=heap[i])break;[heap[p],heap[i]]=[heap[i],heap[p]];i=p;out.push({a:[...heap],active:[i],text:`Bubble ${heap[i]} upward to restore heap order.`,phase:'swap'});}})}else{const nodes=[];arr.forEach(v=>{let i=0;while(nodes[i]!==undefined)i=v<nodes[i]?2*i+1:2*i+2;nodes[i]=v;out.push({a:[...nodes],active:[i],text:`Insert ${v} at ${i===0?'the root':`tree position ${i}`}.`,phase:'insert'});});return out}out.push({a:[...heap],active:[0],text:`Minimum value ${heap[0]} is available at the root.`,phase:'return'});return out}
function dijkstraFrames(){const labels=['A','B','C','D'],edges=[[0,1,4],[0,2,1],[2,1,2],[1,3,1],[2,3,5]],dist=[0,Infinity,Infinity,Infinity],done=[],out=[{a:labels,edges,dist:[...dist],active:[0],visited:[],text:'Set source A to 0; every other distance starts at ∞.',phase:'input'}],adj=labels.map(()=>[]);edges.forEach(([u,v,w])=>adj[u].push([v,w]));while(done.length<labels.length){let u=-1;for(let i=0;i<labels.length;i++)if(!done.includes(i)&&(u<0||dist[i]<dist[u]))u=i;if(u<0||!Number.isFinite(dist[u]))break;done.push(u);out.push({a:labels,edges,dist:[...dist],active:[u],visited:[...done],text:`Settle ${labels[u]} with shortest distance ${dist[u]}.`,phase:'loop'});for(const [v,w] of adj[u])if(dist[u]+w<dist[v]){dist[v]=dist[u]+w;out.push({a:labels,edges,dist:[...dist],active:[u,v],visited:[...done],text:`Relax ${labels[u]} → ${labels[v]}: new distance ${dist[v]}.`,phase:'compare'})}}out.push({a:labels,edges,dist:[...dist],active:[],visited:[...done],text:`Shortest distances: ${dist.join(', ')}.`,phase:'return'});return out}
const detailedBuildFrames=buildFrames;
buildFrames=()=>{const custom={array:arrayFrames,linked:linkedFrames,deque:dequeFrames,hash:hashFrames,bst:a=>treeInsertFrames(a,'bst'),heap:a=>treeInsertFrames(a,'heap'),dijkstra:dijkstraFrames};if(!custom[selected.id])return detailedBuildFrames();frames=custom[selected.id](values);index=0;renderFrame()};
const detailedVisualMarkup=visualMarkup;
visualMarkup=f=>{if(selected.id==='hash')return `<div class="avs-hash-view">${f.a.map((v,i)=>`<div class="avs-hash-bucket${f.active.includes(i)?' active':''}"><small>BUCKET ${i}</small><strong>${v}</strong></div>`).join('')}</div>`;if(selected.id==='dijkstra'){const pos=[[18,50],[43,20],[43,80],[78,50]],visited=new Set(f.visited||[]);return `<div class="avs-graph-view"><svg viewBox="0 0 100 100" preserveAspectRatio="none">${f.edges.map(([a,b,w])=>`<line x1="${pos[a][0]}" y1="${pos[a][1]}" x2="${pos[b][0]}" y2="${pos[b][1]}" class="${visited.has(a)&&visited.has(b)?'visited':''}"/><text x="${(pos[a][0]+pos[b][0])/2}" y="${(pos[a][1]+pos[b][1])/2-2}">${w}</text>`).join('')}</svg>${f.a.map((v,i)=>`<div class="avs-graph-node${f.active.includes(i)?' active':''}${visited.has(i)?' visited':''}" style="left:${pos[i][0]}%;top:${pos[i][1]}%"><small>${Number.isFinite(f.dist[i])?f.dist[i]:'∞'}</small>${v}</div>`).join('')}<div class="avs-graph-legend"><span>● Current</span><span>● Settled</span></div></div>`}return detailedVisualMarkup(f)};
const detailedOutput=programOutput;
programOutput=()=>{if(selected.id==='array')return `Array after append: ${[...values,99].join(' ')}\nIndex 0: ${values[0]}\n\nProcess finished successfully.`;if(selected.id==='linked')return `Linked list: ${values.join(' → ')} → NULL\n\nProcess finished successfully.`;if(selected.id==='deque'){const d=[];values.forEach((v,i)=>i%2?d.unshift(v):d.push(v));const front=d.shift(),rear=d.pop();return `Deque: ${d.join(' ⇄ ')}\nPopped front: ${front}\nPopped rear : ${rear}\n\nProcess finished successfully.`}if(selected.id==='hash'){const freq={};values.forEach(v=>freq[v]=(freq[v]||0)+1);return `Frequency table:\n${Object.keys(freq).sort((a,b)=>a-b).map(k=>`${k} => ${freq[k]}`).join('\n')}\n\nProcess finished successfully.`}if(selected.id==='bst')return `Inorder traversal: ${[...values].sort((a,b)=>a-b).join(' ')}\n\nProcess finished successfully.`;if(selected.id==='heap')return `Min-heap removal order: ${[...values].sort((a,b)=>a-b).join(' ')}\n\nProcess finished successfully.`;if(selected.id==='dijkstra')return `Source: A\nA: 0\nB: 3\nC: 1\nD: 4\n\nProcess finished successfully.`;return detailedOutput()};
selectTopic('bubble');
})();
