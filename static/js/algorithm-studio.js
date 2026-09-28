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
    g[u].each { |v| seen[v]=true; q << v unless seen[v] }
  end
  order
end`}
};
const generic={
python:t=>`# ${t.name}\ndef solve(values):\n    # Implement ${t.name} using the steps below\n    result = list(values)\n    return result`,
cpp:t=>`// ${t.name}\nvector<int> solve(const vector<int>& values) {\n    vector<int> result = values;\n    return result;\n}`,
java:t=>`// ${t.name}\nstatic int[] solve(int[] values) {\n    int[] result = values.clone();\n    return result;\n}`,
ruby:t=>`# ${t.name}\ndef solve(values)\n  result = values.dup\n  result\nend`
};
let selected=topics[0],filter='all',values=[8,3,5,1,9,2],frames=[],index=0,timer=null;
function sortFrames(arr,type){const a=[...arr],out=[{a:[...a],active:[],text:'Initial array'}];if(type==='selection'){for(let i=0;i<a.length;i++){let m=i;for(let j=i+1;j<a.length;j++){out.push({a:[...a],active:[m,j],text:`Compare minimum ${a[m]} with ${a[j]}`});if(a[j]<a[m])m=j;}[a[i],a[m]]=[a[m],a[i]];out.push({a:[...a],active:[i],done:i+1,text:`Place ${a[i]} at index ${i}`});}}else if(type==='insertion'){for(let i=1;i<a.length;i++){let j=i;while(j>0&&a[j-1]>a[j]){out.push({a:[...a],active:[j-1,j],text:'Shift the larger value right'});[a[j-1],a[j]]=[a[j],a[j-1]];j--;}out.push({a:[...a],active:[j],done:i+1,text:'Key inserted into sorted prefix'});}}else{for(let end=a.length-1;end>0;end--)for(let i=0;i<end;i++){out.push({a:[...a],active:[i,i+1],text:`Compare ${a[i]} and ${a[i+1]}`});if(a[i]>a[i+1]){[a[i],a[i+1]]=[a[i+1],a[i]];out.push({a:[...a],active:[i,i+1],text:'Swap the out-of-order pair'});}}}out.push({a:[...a],active:[],done:a.length,text:'Complete'});return out}
function simpleFrames(arr){return arr.map((_,i)=>({a:[...arr],active:[i],done:i,text:`Inspect index ${i}: value ${arr[i]}`})).concat({a:[...arr],active:[],done:arr.length,text:'Traversal complete'})}
function buildFrames(){const visual=['bubble','selection','insertion'].includes(selected.id)?sortFrames(values,selected.id):simpleFrames(selected.id==='binary'?[...values].sort((a,b)=>a-b):values);frames=visual;index=0;renderFrame()}
function renderFrame(){const f=frames[index]||{a:values,active:[]};$('avsCanvas').innerHTML=f.a.map((v,i)=>`<div class="${selected.kind==='structure'?'avs-node':'avs-bar'} ${f.active.includes(i)?'active':''} ${i<(f.done||0)?'done':''}" style="--v:${Math.max(1,Math.min(10,Math.abs(v)))}"><span>${v}</span></div>`).join('');$('avsNarration').querySelector('span').textContent=f.text;$('avsStepCount').textContent=`Step ${index+1} / ${frames.length}`}
function renderTopics(){const q=$('avsSearch').value.toLowerCase();$('avsTopicList').innerHTML=topics.filter(t=>(filter==='all'||t.kind===filter)&&t.name.toLowerCase().includes(q)).map(t=>`<button class="avs-topic-item ${t.id===selected.id?'active':''}" data-id="${t.id}"><i class="bi ${t.icon}"></i><span>${t.name}</span><small>${t.group}</small></button>`).join('');document.querySelectorAll('.avs-topic-item').forEach(b=>b.onclick=()=>selectTopic(b.dataset.id))}
function selectTopic(id){selected=topics.find(t=>t.id===id)||topics[0];$('avsCategory').textContent=(selected.kind==='structure'?'DATA STRUCTURE':'ALGORITHM')+' · '+selected.group.toUpperCase();$('avsTitle').textContent=selected.name;$('avsDescription').textContent=selected.desc;$('avsBest').textContent=selected.best;$('avsAverage').textContent=selected.avg;$('avsWorst').textContent=selected.worst;$('avsSpace').textContent=selected.space;$('avsExplanation').innerHTML=selected.steps.map(x=>`<li>${x}</li>`).join('');renderTopics();renderCode();buildFrames()}
function renderCode(){const lang=$('avsLanguage').value;const template=(code[selected.id]&&code[selected.id][lang])||generic[lang](selected);$('avsCode').textContent=template;$('avsLanguageLabel').textContent=({cpp:'C++',python:'Python',java:'Java',ruby:'Ruby'})[lang]+' · Clean implementation'}
function parseValues(){const a=$('avsInput').value.split(/[ ,]+/).map(Number).filter(Number.isFinite).slice(0,14);if(a.length)values=a;buildFrames()}
function stop(){clearInterval(timer);timer=null;$('avsPlay').innerHTML='<i class="bi bi-play-fill"></i><span>Play</span>'}
$('avsPlay').onclick=()=>{if(timer){stop();return}$('avsPlay').innerHTML='<i class="bi bi-pause-fill"></i><span>Pause</span>';timer=setInterval(()=>{if(index>=frames.length-1){stop();return}index++;renderFrame()},1500-+$('avsSpeed').value)};
$('avsNext').onclick=()=>{stop();index=Math.min(frames.length-1,index+1);renderFrame()};$('avsPrev').onclick=()=>{stop();index=Math.max(0,index-1);renderFrame()};$('avsReset').onclick=()=>{stop();index=0;renderFrame()};$('avsApply').onclick=parseValues;$('avsRandom').onclick=()=>{$('avsInput').value=Array.from({length:7},()=>1+Math.floor(Math.random()*9)).join(', ');parseValues()};$('avsLanguage').onchange=renderCode;$('avsSearch').oninput=renderTopics;document.querySelectorAll('.avs-tabs button').forEach(b=>b.onclick=()=>{document.querySelectorAll('.avs-tabs button').forEach(x=>x.classList.remove('active'));b.classList.add('active');filter=b.dataset.kind;renderTopics()});$('avsCopy').onclick=async()=>{await navigator.clipboard.writeText($('avsCode').textContent);$('avsCopy').innerHTML='<i class="bi bi-check2"></i> Copied';setTimeout(()=>$('avsCopy').innerHTML='<i class="bi bi-copy"></i> Copy',1200)};
selectTopic('bubble');
})();
