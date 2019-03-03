import sys
import os
import time

sys.path.append('/Users/kevin/Desktop/CS7641/HW2/CODE/ABAGAIL.jar')
import java.io.FileReader as FileReader
import java.io.File as File
import java.lang.String as String
import java.lang.StringBuffer as StringBuffer
import java.lang.Boolean as Boolean
import java.util.Random as Random

import dist.DiscreteDependencyTree as DiscreteDependencyTree
import dist.DiscreteUniformDistribution as DiscreteUniformDistribution
import dist.Distribution as Distribution
import opt.DiscreteChangeOneNeighbor as DiscreteChangeOneNeighbor
import opt.EvaluationFunction as EvaluationFunction
import opt.GenericHillClimbingProblem as GenericHillClimbingProblem
import opt.HillClimbingProblem as HillClimbingProblem
import opt.NeighborFunction as NeighborFunction
import opt.RandomizedHillClimbing as RandomizedHillClimbing
import opt.SimulatedAnnealing as SimulatedAnnealing
import opt.example.FourPeaksEvaluationFunction as FourPeaksEvaluationFunction
import opt.ga.CrossoverFunction as CrossoverFunction
import opt.ga.SingleCrossOver as SingleCrossOver
import opt.ga.DiscreteChangeOneMutation as DiscreteChangeOneMutation
import opt.ga.GenericGeneticAlgorithmProblem as GenericGeneticAlgorithmProblem
import opt.ga.GeneticAlgorithmProblem as GeneticAlgorithmProblem
import opt.ga.MutationFunction as MutationFunction
import opt.ga.StandardGeneticAlgorithm as StandardGeneticAlgorithm
import opt.ga.UniformCrossOver as UniformCrossOver
import opt.prob.GenericProbabilisticOptimizationProblem as GenericProbabilisticOptimizationProblem
import opt.prob.MIMIC as MIMIC
import opt.prob.ProbabilisticOptimizationProblem as ProbabilisticOptimizationProblem
import shared.FixedIterationTrainer as FixedIterationTrainer
import opt.example.ContinuousPeaksEvaluationFunction as ContinuousPeaksEvaluationFunction
import opt.example.KnapsackEvaluationFunction as KnapsackEvaluationFunction
from array import array
from time import clock
from itertools import product

"""
Commandline parameter(s):
   none
"""

# Random number generator */
random = Random()
# The number of items
NUM_ITEMS = 40
# The number of copies each
COPIES_EACH = 4
# The maximum weight for a single element
MAX_WEIGHT = 50
# The maximum volume for a single element
MAX_VOLUME = 50
# The volume of the knapsack
KNAPSACK_VOLUME = MAX_VOLUME * NUM_ITEMS * COPIES_EACH * .4

# create copies
fill = [COPIES_EACH] * NUM_ITEMS
copies = array('i', fill)

# create weights and volumes
fill = [0] * NUM_ITEMS
weights = array('d', fill)
volumes = array('d', fill)
for i in range(0, NUM_ITEMS):
    weights[i] = random.nextDouble() * MAX_WEIGHT
    volumes[i] = random.nextDouble() * MAX_VOLUME

# create range
fill = [COPIES_EACH + 1] * NUM_ITEMS
ranges = array('i', fill)

numTrials = 1
maxIters = 5000
outfile = './KS_@ALG@_@N@_LOG.csv'
ef = KnapsackEvaluationFunction(weights, volumes, KNAPSACK_VOLUME, copies)
odd = DiscreteUniformDistribution(ranges)
nf = DiscreteChangeOneNeighbor(ranges)
mf = DiscreteChangeOneMutation(ranges)
cf = UniformCrossOver()
df = DiscreteDependencyTree(.1, ranges)
hcp = GenericHillClimbingProblem(ef, odd, nf)
gap = GenericGeneticAlgorithmProblem(ef, odd, mf, cf)
pop = GenericProbabilisticOptimizationProblem(ef, odd, df)

#MIMIC
for t in range(numTrials):
    for samples,keep,m in product([100],[50],[0.1,0.3,0.5,0.7,0.9]):
        fname = outfile.replace('@ALG@','MIMIC{}_{}_{}'.format(samples,keep,m)).replace('@N@',str(t+1))
        with open(fname,'w') as f:
            f.write('iterations,fitness,time\n')
        df = DiscreteDependencyTree(m, ranges)
        pop = GenericProbabilisticOptimizationProblem(ef, odd, df)
        mimic = MIMIC(samples, keep, pop)
        fit = FixedIterationTrainer(mimic, 10)
        times =[0]
        for i in range(0,maxIters,10):
            start = clock()
            fit.train()
            elapsed = time.clock()-start
            times.append(times[-1]+elapsed)
#           fevals = ef.fevals
            score = ef.value(mimic.getOptimal())
#           ef.fevals -= 1
            st = '{},{},{}\n'.format(i,score,times[-1])
            print st
            with open(fname,'a') as f:
                f.write(st)

# RHC
for t in range(numTrials):
    fname = outfile.replace('@ALG@','RHC').replace('@N@',str(t+1))
    with open(fname,'w') as f:
        f.write('iterations,fitness,time\n')
    rhc = RandomizedHillClimbing(hcp)
    fit = FixedIterationTrainer(rhc, 10)
    times =[0]
    for i in range(0,maxIters,10):
        start = clock()
        fit.train()
        elapsed = time.clock()-start
        times.append(times[-1]+elapsed)
#       fevals = ef.fevals
        score = ef.value(rhc.getOptimal())
#       ef.fevals -= 1
        st = '{},{},{}\n'.format(i,score,times[-1])
        print st
        with open(fname,'a') as f:
            f.write(st)



# SA
for t in range(numTrials):
    for CE in [0.15,0.35,0.55,0.75,0.95]:
        fname = outfile.replace('@ALG@','SA{}'.format(CE)).replace('@N@',str(t+1))
        with open(fname,'w') as f:
            f.write('iterations,fitness,time\n')
        sa = SimulatedAnnealing(1E10, CE, hcp)
        fit = FixedIterationTrainer(sa, 10)
        times =[0]
        for i in range(0,maxIters,10):
            start = clock()
            fit.train()
            elapsed = time.clock()-start
            times.append(times[-1]+elapsed)
#           fevals = ef.fevals
            score = ef.value(sa.getOptimal())
#           ef.fevals -= 1
            st = '{},{},{}\n'.format(i,score,times[-1])
            print st
            with open(fname,'a') as f:
                f.write(st)

#GA
for t in range(numTrials):
    for popu,mate,mutate in product([100],[50,30,10],[30,10]):
        fname = outfile.replace('@ALG@','GA{}_{}_{}'.format(popu,mate,mutate)).replace('@N@',str(t+1))
        with open(fname,'w') as f:
            f.write('iterations,fitness,time\n')
        ga = StandardGeneticAlgorithm(popu, mate, mutate, gap)
        fit = FixedIterationTrainer(ga, 10)
        times =[0]
        for i in range(0,maxIters,10):
            start = clock()
            fit.train()
            elapsed = time.clock()-start
            times.append(times[-1]+elapsed)
#           fevals = ef.fevals
            score = ef.value(ga.getOptimal())
#           ef.fevals -= 1
            st = '{},{},{}\n'.format(i,score,times[-1])
            print st
            with open(fname,'a') as f:
                f.write(st)