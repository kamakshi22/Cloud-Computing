#!/usr/bin/env python

from mrjob.job import MRJob
from mrjob.step import MRStep
import copy
import json
import re



class MRPageRank(MRJob):
    def steps(self):
        return [
            MRStep(mapper=self.mapper_get_total_nodes,
                    reducer=self.reducer_get_total_nodes),
            MRStep(mapper=self.mapper_get_nodes,
                    reducer=self.reducer_get_nodes),
            MRStep(mapper=self.mapper_inital,
                   combiner=self.reducer_inital,
                    reducer=self.reducer_inital),
            MRStep(reducer=self.reducer_inital),
            MRStep(reducer=self.reducer_inital),
            MRStep(reducer=self.reducer_inital),
            MRStep(reducer=self.reducer_inital),
            MRStep(reducer=self.reducer_inital),
            MRStep(reducer=self.reducer_inital),
            MRStep(reducer=self.reducer_inital),
            MRStep(reducer=self.reducer_inital),
            MRStep(reducer=self.reducer_inital),
            MRStep(reducer=self.reducer_inital),
            MRStep(reducer=self.reducer_inital),
            MRStep(reducer=self.reducer_inital),
            MRStep(reducer=self.reducer_inital),
            MRStep(reducer=self.reducer_inital),
            

            MRStep(reducer=self.reducer_final_merge),
            MRStep(reducer=self.reducer_final_display)
        ]

    def mapper_get_total_nodes(self, _, line):
        if line.find('Nodes:') > 0:
            nodes = float(line[line.find('Nodes:')+len('Nodes:'):line.find('Edge')].strip())
            yield None, ('total_nodes:',nodes)
        elif line[0] != '#':
            yield None, line
        else:
            pass

    def reducer_get_total_nodes(self, node, lines):
        yield node, list(lines)

    
    def mapper_get_nodes(self, _, lines):
        total_node = [float(total[1]) for total in lines if 'total_nodes:' in total]

        for link in lines:
            if type(link) is not list and len(total_node) > 0:
                y, x = link.split('\t')                   # y: from node Id, x: to node Id
                yield (int(y),total_node[0]), int(x)

    def reducer_get_nodes(self, y, x):
        yield  y, list(x)

    def mapper_inital(self, y, x):
        y_out = float(len(x))
        pr_y = (1.0/y[1])
        yield y, x
        for c in x:
            yield (c,y[1]), pr_y/y_out

    # x: contains list of probabilites and out-links for y node id
    def reducer_inital(self, y, x):
        damping_factor = 0.85
        out_links = []
        page_ranks = 0
        for p in x:
            if(isinstance(p, float)):
                page_ranks += p
            else:
                # node
                yield y, p
                out_links += p

        new_pr_x = ((1-damping_factor)/y[1]) + (damping_factor*page_ranks)
        
        for c in out_links:
            if page_ranks != 0:
                yield (c, y[1]), (new_pr_x / len(out_links))


    def reducer_final_merge(self,y,x):
        page_ranks = [rank for rank in x if isinstance(rank, float)]
        yield None,(sum(page_ranks),y[0])

    def reducer_final_display(self,_,node):
        index = 0
        result = []
        nodes = sorted(list(node), key=lambda x: float(x[0]), reverse=True)
        for s in nodes:
            #yield (s[0], s[1]) 
            index += 1
            if index < 11:
                yield (s[0], s[1])
            else:
                break

if __name__ == '__main__':
    MRPageRank.run()
