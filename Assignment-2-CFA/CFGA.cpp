/**
 * ICFG.cpp
 * @author kisslune 
 */

#include "CFGA.h"
#include <functional>
#include <utility>

using namespace SVF;
using namespace llvm;
using namespace std;

int main(int argc, char **argv)
{
    auto moduleNameVec =
            OptionBase::parseOptions(argc, argv, "Whole Program Points-to Analysis",
                                     "[options] <input-bitcode...>");

    LLVMModuleSet::buildSVFModule(moduleNameVec);

    SVFIRBuilder builder;
    auto pag = builder.build();
    auto icfg = pag->getICFG();

    CFGAnalysis analyzer = CFGAnalysis(icfg);

    analyzer.analyze(icfg);

    analyzer.dumpPaths();
    LLVMModuleSet::releaseLLVMModuleSet();
    return 0;
}


void CFGAnalysis::analyze(SVF::ICFG *icfg)
{
    reachablePaths.clear();
    callStack = std::stack<unsigned>();

    // Sources and sinks are specified when an analyzer is instantiated.
    for (auto src : sources)
        for (auto snk : sinks)
        {
            std::vector<unsigned> path;
            // Keep visited states on the current path, not across DFS branches.
            // The same function may be visited again from a different call site.
            using State = std::pair<unsigned, std::stack<unsigned>>;
            std::set<State> activeStates;
            std::set<unsigned> activeCalls;

            std::function<void(const ICFGNode*)> dfs = [&](const ICFGNode* node)
            {
                const State state(node->getId(), callStack);
                if (!activeStates.insert(state).second)
                    return;
                path.push_back(node->getId());

                if (node->getId() == snk)
                {
                    if (callStack.empty())
                        recordPath(path);
                }
                else
                {
                    for (const auto* edge : node->getOutEdges())
                    {
                        if (const auto* call = dyn_cast<CallCFGEdge>(edge))
                        {
                            const unsigned callSite = call->getCallSite()->getId();
                            // Bound recursion: do not repeat a call site while it
                            // is still active. Otherwise the set of paths is infinite.
                            if (!activeCalls.insert(callSite).second)
                                continue;
                            callStack.push(callSite);
                            dfs(edge->getDstNode());
                            callStack.pop();
                            activeCalls.erase(callSite);
                        }
                        else if (const auto* ret = dyn_cast<RetCFGEdge>(edge))
                        {
                            const unsigned callSite = ret->getCallSite()->getId();
                            if (callStack.empty() || callStack.top() != callSite)
                                continue;
                            callStack.pop();
                            activeCalls.erase(callSite);
                            dfs(edge->getDstNode());
                            callStack.push(callSite);
                            activeCalls.insert(callSite);
                        }
                        else if (edge->isIntraCFGEdge())
                        {
                            dfs(edge->getDstNode());
                        }
                    }
                }

                path.pop_back();
                activeStates.erase(state);
            };

            dfs(icfg->getICFGNode(src));
        }
}
