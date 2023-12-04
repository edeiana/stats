#include "llvm/Pass.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "llvm/IR/LegacyPassManager.h"
#include <utils.hpp>

using namespace llvm;

namespace {

struct CAT : public ModulePass {

  static char ID;

  CAT() : ModulePass(ID) {}

  bool runOnModule(Module &M) override {
    bool modified = false;

    return modified;
  }

  void getAnalysisUsage(AnalysisUsage &AU) const override {
    return ;
  }

}; 

}

char CAT::ID = 0;
static RegisterPass<CAT> X("CAT", "CAT pass");

// Next there is code to register your pass to "clang"
static CAT * _PassMaker = NULL;
static RegisterStandardPasses _RegPass1(PassManagerBuilder::EP_OptimizerLast,
    [](const PassManagerBuilder&, legacy::PassManagerBase& PM) {
        if(!_PassMaker){ PM.add(_PassMaker = new CAT());}}); // ** for -Ox
static RegisterStandardPasses _RegPass2(PassManagerBuilder::EP_EnabledOnOptLevel0,
    [](const PassManagerBuilder&, legacy::PassManagerBase& PM) {
        if(!_PassMaker){ PM.add(_PassMaker = new CAT()); }}); // ** for -O0

