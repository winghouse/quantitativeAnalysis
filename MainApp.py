from Biance.thread.KLineAnalysisThread import KLineAnalysisThread

if __name__ == '__main__':
    klineAnalysis = KLineAnalysisThread("KLineAnalysis")
    klineAnalysis.start()
